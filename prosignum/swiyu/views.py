import qrcode
import io
import base64
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from .models import SwiyuVerification, SwiyuUserProfile
from .swiyu_service import SwiyuVerifierService
from core.models import Participant


def swiyu_login_page(request):
    """Display the Swiyu E-ID login page with QR code"""

    if request.user.is_authenticated:
        return redirect('/')

    try:
        # Create verification request
        service = SwiyuVerifierService()
        verification_id, verification_url = service.create_verification_request(
            purpose="Login to Prosignum"
        )

        # Store verification in database
        timeout = getattr(settings, 'SWIYU_VERIFICATION_TIMEOUT', 300)
        expires_at = timezone.now() + timedelta(seconds=timeout)
        verification = SwiyuVerification.objects.create(
            verification_id=verification_id,
            verification_url=verification_url,
            status='pending',
            expires_at=expires_at
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for embedding in HTML
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        poll_interval = getattr(settings, 'SWIYU_POLL_INTERVAL', 2)

        context = {
            'verification_id': str(verification.id),
            'qr_code': qr_code_base64,
            'expires_in': timeout,
            'poll_interval': poll_interval,
        }

        return render(request, 'swiyu/login.html', context)

    except Exception as e:
        return render(request, 'swiyu/error.html', {'error': str(e)})


@require_http_methods(["GET"])
def swiyu_check_status(request, verification_uuid):
    """AJAX endpoint to check verification status"""

    try:
        verification = SwiyuVerification.objects.get(id=verification_uuid)

        # Check if expired
        if timezone.now() > verification.expires_at:
            verification.status = 'expired'
            verification.save()
            return JsonResponse({
                'status': 'expired',
                'message': 'Verification request expired'
            })

        # If already completed or failed, return cached status
        if verification.status in ['completed', 'failed']:
            return JsonResponse({
                'status': verification.status,
                'redirect': '/' if verification.status == 'completed' else None
            })

        # Check with Swiyu API
        service = SwiyuVerifierService()
        result = service.check_verification_status(verification.verification_id)

        if result['status'] == 'completed':
            # Verification successful
            verification.status = 'completed'
            verification.verified_claims = result['verified_claims']
            verification.save()

            # Authenticate user
            user = _get_or_create_user_from_claims(result['verified_claims'])
            login(request, user)

            return JsonResponse({
                'status': 'completed',
                'redirect': '/'
            })

        elif result['status'] == 'failed':
            verification.status = 'failed'
            verification.error_code = result.get('error')
            verification.save()

            return JsonResponse({
                'status': 'failed',
                'error': result.get('error')
            })

        else:
            # Still pending
            return JsonResponse({
                'status': 'pending'
            })

    except SwiyuVerification.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Verification not found'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def _get_or_create_user_from_claims(claims: dict) -> User:
    """
    Get or create a Django user from Swiyu verified claims
    """

    # Create unique hash of E-ID claims
    service = SwiyuVerifierService()
    eid_hash = service.hash_eid_claims(claims)

    # Try to find existing user with this E-ID
    try:
        swiyu_profile = SwiyuUserProfile.objects.get(eid_hash=eid_hash)
        user = swiyu_profile.user

        # Update last verified timestamp
        swiyu_profile.last_verified = timezone.now()
        swiyu_profile.save()

        # Ensure Participant exists (for users created before this update)
        if not hasattr(user, 'participant_profile'):
            Participant.objects.create(
                user=user,
                swiyu_profile=swiyu_profile,
                ahv_number=claims.get('personal_administrative_number', '')
            )
        else:
            # Update AHV number if missing
            participant = user.participant_profile
            if not participant.ahv_number and claims.get('personal_administrative_number'):
                participant.ahv_number = claims.get('personal_administrative_number')
                participant.save()

        return user

    except SwiyuUserProfile.DoesNotExist:
        # Create new user
        username = f"swiyu_{eid_hash[:12]}"

        user = User.objects.create_user(
            username=username,
            first_name=claims.get('given_name', ''),
            last_name=claims.get('family_name', ''),
        )

        # Create Swiyu profile
        swiyu_profile = SwiyuUserProfile.objects.create(
            user=user,
            given_name=claims['given_name'],
            family_name=claims['family_name'],
            birth_date=claims['birth_date'],
            birth_place=claims.get('birth_place', ''),
            eid_hash=eid_hash
        )

        # Create Participant profile linked to user and swiyu profile
        Participant.objects.create(
            user=user,
            swiyu_profile=swiyu_profile,
            ahv_number=claims.get('personal_administrative_number', '')
        )

        return user

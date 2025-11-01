from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from .models import Initiative, Participant, Signature, Municipality


def home(request):
    """Homepage view"""
    now = timezone.now()

    # Get all active initiatives within collection period
    initiatives = Initiative.objects.filter(
        status='active',
        collection_start_date__lte=now,
        collection_end_date__gte=now
    ).order_by('-created_at')

    # Get set of initiative IDs the user has already signed
    signed_initiative_ids = set()
    if request.user.is_authenticated:
        try:
            participant = request.user.participant_profile
            signed_initiative_ids = set(
                Signature.objects.filter(participant=participant)
                .values_list('initiative_id', flat=True)
            )
        except Participant.DoesNotExist:
            pass

    # Annotate each initiative with already_signed flag
    for initiative in initiatives:
        initiative.already_signed = initiative.id in signed_initiative_ids

    return render(request, 'core/home.html', {
        'initiatives': initiatives,
    })


@login_required
def profile(request):
    """User profile view"""
    return render(request, 'core/profile.html')


def logout_view(request):
    """Logout view"""
    auth_logout(request)
    return redirect('home')


def legal_notice(request):
    """Legal notice page"""
    return render(request, 'pages/legal.html')


def impressum(request):
    """Impressum page"""
    return render(request, 'pages/impressum.html')


def contact(request):
    """Contact page"""
    return render(request, 'pages/contact.html')


@login_required
def sign_initiative(request, initiative_id):
    """Sign an initiative"""
    initiative = get_object_or_404(Initiative, id=initiative_id)

    # Check if initiative is active and collecting
    if not initiative.is_collecting():
        messages.error(request, _("This initiative is not currently accepting signatures."))
        return redirect('home')

    # Get participant profile
    try:
        participant = request.user.participant_profile
    except Participant.DoesNotExist:
        messages.error(request, _("Participant profile not found. Please contact support."))
        return redirect('home')

    # Check if already signed
    existing_signature = Signature.objects.filter(
        initiative=initiative,
        participant=participant
    ).first()

    if existing_signature:
        messages.info(request, _("You have already signed this initiative."))
        return redirect('home')

    if request.method == 'POST':
        # Get municipality from form
        municipality_id = request.POST.get('municipality')
        street_and_number = request.POST.get('street_and_number', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()

        if not municipality_id or not street_and_number or not postal_code:
            messages.error(request, _("Please fill in all required fields."))
            return render(request, 'core/sign_initiative.html', {
                'initiative': initiative,
                'municipalities': Municipality.objects.all().order_by('name')
            })

        municipality = get_object_or_404(Municipality, id=municipality_id)

        # Create signature
        Signature.objects.create(
            initiative=initiative,
            participant=participant,
            municipality=municipality,
            given_name=participant.swiyu_profile.given_name,
            family_name=participant.swiyu_profile.family_name,
            birth_date=participant.swiyu_profile.birth_date,
            street_and_number=street_and_number,
            postal_code=postal_code,
            status='pending'
        )

        messages.success(request, _("Your signature has been submitted and is pending review by your municipality."))
        return redirect('home')

    # GET request - show signing form
    municipalities = Municipality.objects.all().order_by('name')

    # Build PLZ to municipality mapping for JavaScript
    import json
    plz_to_municipality = {}
    for municipality in municipalities:
        if municipality.postal_code:
            plz = municipality.postal_code
            if plz not in plz_to_municipality:
                plz_to_municipality[plz] = []
            plz_to_municipality[plz].append({
                'id': municipality.id,
                'name': municipality.name,
                'canton': municipality.canton,
                'display': f"{municipality.name} ({municipality.canton})"
            })

    return render(request, 'core/sign_initiative.html', {
        'initiative': initiative,
        'municipalities': municipalities,
        'plz_to_municipality_json': json.dumps(plz_to_municipality),
    })

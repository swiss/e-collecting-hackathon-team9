import hashlib
import requests
import logging
from typing import Dict, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


class SwiyuVerifierService:
    """Real Swiyu verifier service client"""

    def __init__(self):
        self.api_url = settings.SWIYU_VERIFIER_API_URL

    def create_verification_request(self, purpose: str = "User Authentication") -> Tuple[str, str]:
        """
        Create a verification request with Swiyu Generic Verifier

        Returns:
            Tuple of (verification_id, verification_url)
        """
        # Define presentation definition for Swiss E-ID (BetaId)
        presentation_definition = {
            "id": "swiss-eid-auth",
            "name": "Swiss E-ID Authentication",
            "purpose": purpose,
            "input_descriptors": [
                {
                    "id": "swiss-eid-credential",
                    "format": {
                        "vc+sd-jwt": {
                            "sd-jwt_alg_values": ["ES256"],
                            "kb-jwt_alg_values": ["ES256"]
                        }
                    },
                    "constraints": {
                        "fields": [
                            {"path": ["$.family_name"]},
                            {"path": ["$.given_name"]},
                            {"path": ["$.birth_date"]},
                            {"path": ["$.personal_administrative_number"]},
                            {
                                "path": ["$.vct"],
                                "filter": {
                                    "type": "string",
                                    "const": "betaid-sdjwt"
                                }
                            }
                        ]
                    }
                }
            ]
        }

        payload = {
            "accepted_issuer_dids": [],  # Accept any official Swiss issuer
            "jwt_secured_authorization_request": True,
            "presentation_definition": presentation_definition
        }

        try:
            response = requests.post(
                f"{self.api_url}/management/api/verifications",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            verification_id = data['id']  # New API uses 'id' not 'verification_id'
            verification_url = data['verification_url']

            logger.info(f"Created verification request: {verification_id}")
            return verification_id, verification_url

        except requests.exceptions.RequestException as e:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = f" - Response: {e.response.text}"
                except:
                    pass
            logger.error(f"Failed to create verification request: {e}{error_detail}")
            raise Exception(f"Failed to communicate with Swiyu verifier: {str(e)}{error_detail}")

    def check_verification_status(self, verification_id: str) -> Dict:
        """
        Check the status of a verification request

        Returns:
            Dict with status and verified_claims (if completed)
        """
        try:
            response = requests.get(
                f"{self.api_url}/management/api/verifications/{verification_id}",
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            # Map new API response format to expected format
            state = data.get('state', '').lower()  # Convert PENDING/FAILED/SUCCESS
            # Map SUCCESS to completed for Django compatibility
            if state == 'success':
                state = 'completed'

            # Extract error from wallet_response if present
            wallet_response = data.get('wallet_response', {})
            error_code = wallet_response.get('error_code') if wallet_response else None

            # Extract verified claims from wallet_response
            verified_claims = None
            if wallet_response and wallet_response.get('credential_subject_data'):
                verified_claims = wallet_response.get('credential_subject_data')

            return {
                'status': state,
                'verified_claims': verified_claims,
                'error': error_code
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check verification status: {e}")
            raise Exception(f"Failed to communicate with Swiyu verifier: {str(e)}")

    @staticmethod
    def hash_eid_claims(claims: Dict) -> str:
        """
        Create a unique hash of E-ID claims for user matching
        Uses personal_administrative_number (AHV) + birth_date + family_name + given_name
        """
        claim_string = (
            f"{claims.get('personal_administrative_number', '')}"
            f"{claims.get('birth_date', '')}"
            f"{claims.get('family_name', '')}"
            f"{claims.get('given_name', '')}"
        )
        return hashlib.sha256(claim_string.encode()).hexdigest()


# Keep mock for local development without Docker
class MockSwiyuService:
    """Mock Swiyu verifier service for development"""

    def __init__(self):
        self._verifications = {}

    def create_verification_request(self, purpose: str = "User Authentication") -> Tuple[str, str]:
        import uuid
        verification_id = str(uuid.uuid4())
        verification_url = f"openid4vp://verify?request_id={verification_id}"

        self._verifications[verification_id] = {
            'status': 'pending',
            'created_at': datetime.now(),
            'purpose': purpose
        }

        return verification_id, verification_url

    def check_verification_status(self, verification_id: str) -> Dict:
        from datetime import datetime
        if verification_id not in self._verifications:
            return {'status': 'failed', 'error': 'verification_not_found'}

        verification = self._verifications[verification_id]
        elapsed = (datetime.now() - verification['created_at']).total_seconds()

        if elapsed > 5 and verification['status'] == 'pending':
            verification['status'] = 'completed'
            verification['verified_claims'] = {
                'given_name': 'Max',
                'family_name': 'Mustermann',
                'birth_date': '1990-01-15',
                'personal_administrative_number': '756.1234.5678.97'
            }

        return {
            'status': verification['status'],
            'verified_claims': verification.get('verified_claims'),
            'error': verification.get('error')
        }

    @staticmethod
    def hash_eid_claims(claims: Dict) -> str:
        claim_string = (
            f"{claims.get('personal_administrative_number', '')}"
            f"{claims.get('birth_date', '')}"
            f"{claims.get('family_name', '')}"
            f"{claims.get('given_name', '')}"
        )
        return hashlib.sha256(claim_string.encode()).hexdigest()

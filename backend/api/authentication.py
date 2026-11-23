import logging
import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError, ExpiredSignatureError
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import User

logger = logging.getLogger(__name__)

_jwks_client = None


def _get_jwks_client():
    global _jwks_client
    if _jwks_client is not None:
        return _jwks_client

    frontend_api = getattr(settings, 'CLERK_FRONTEND_API', '') or ''
    if not frontend_api:
        import base64
        pk = getattr(settings, 'CLERK_PUBLISHABLE_KEY', '') or ''
        if pk:
            try:
                b64_part = pk.split('_', 2)[-1]
                b64_part += '=' * (-len(b64_part) % 4)
                frontend_api = base64.b64decode(b64_part).decode('utf-8').rstrip('$')
            except Exception:
                pass

    if not frontend_api:
        raise AuthenticationFailed(
            'Server misconfiguration: CLERK_FRONTEND_API or '
            'CLERK_PUBLISHABLE_KEY must be set for JWT verification.'
        )

    if not frontend_api.startswith('https://'):
        frontend_api = f'https://{frontend_api}'

    jwks_url = f'{frontend_api}/.well-known/jwks.json'
    _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_client


class ClerkAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1].strip()
        if not token:
            return None

        try:
            jwks_client = _get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=['RS256'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True,
                },
            )

            clerk_user_id = payload.get('sub')
            if not clerk_user_id:
                raise AuthenticationFailed('Token payload missing subject claim')

            user = User.objects.filter(clerk_user_id=clerk_user_id).first()
            if not user:
                user = self._sync_clerk_user(clerk_user_id)

            if not user:
                raise AuthenticationFailed('Could not resolve or create user profile')
            user._id = user.id
            return (user, token)

        except ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except PyJWTError as e:
            raise AuthenticationFailed(f'Invalid token: {e}') from e
        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.exception('Unexpected authentication error: %s', e)
            raise AuthenticationFailed('Authentication error') from e

    def authenticate_header(self, request):
        return 'Bearer realm="api"'

    def _sync_clerk_user(self, clerk_user_id):
        secret_key = getattr(settings, 'CLERK_SECRET_KEY', None)
        if not secret_key:
            return None

        try:
            res = requests.get(
                f'https://api.clerk.com/v1/users/{clerk_user_id}',
                headers={'Authorization': f'Bearer {secret_key}'},
                timeout=5
            )
            if res.status_code != 200:
                return None

            data = res.json()
            email_addresses = data.get('email_addresses', [])
            primary_id = data.get('primary_email_address_id')
            email = None

            for email_obj in email_addresses:
                if email_obj.get('id') == primary_id:
                    email = email_obj.get('email_address')
                    break
            if not email and email_addresses:
                email = email_addresses[0].get('email_address')

            if not email:
                return None

            first_name = data.get('first_name') or ''
            last_name = data.get('last_name') or ''
            name = f"{first_name} {last_name}".strip() or email.split('@')[0]
            role = 'seller' if data.get('unsafe_metadata', {}).get('role') == 'seller' else 'customer'
            phone = data.get('unsafe_metadata', {}).get('phone') or None

            user = User.objects.filter(email__iexact=email).first()
            if user:
                user.clerk_user_id = clerk_user_id
                user.save(update_fields=['clerk_user_id'])
                return user

            user = User.objects.create(
                clerk_user_id=clerk_user_id,
                name=name,
                email=email,
                role=role,
                phone=phone
            )
            return user
        except Exception:
            return None

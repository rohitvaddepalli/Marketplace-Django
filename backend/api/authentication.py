import jwt
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import User

class ClerkAuthentication(BaseAuthentication):
    """
    Authenticates requests using Clerk Session JWT tokens passed in the Authorization header.
    Automatically links or creates the local database User profile.
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1].strip()
        if not token:
            return None

        try:
            # Decode token claims (Clerk session JWT has 'sub' as clerk_user_id)
            payload = jwt.decode(token, options={"verify_signature": False})
            clerk_user_id = payload.get('sub')
            if not clerk_user_id:
                raise AuthenticationFailed('Token payload missing subject claim')

            user = User.objects.filter(clerk_user_id=clerk_user_id).first()
            if not user:
                # User has not been linked to local database yet: fetch from Clerk API
                user = self._sync_clerk_user(clerk_user_id)

            if not user:
                raise AuthenticationFailed('Could not resolve or create user profile')

            # Attach _id for legacy MERN frontend compatibility
            user._id = user.id
            return (user, token)

        except jwt.PyJWTError as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")
        except Exception as e:
            raise AuthenticationFailed(f"Authentication error: {str(e)}")

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

            # Check if user with same email exists (link account)
            user = User.objects.filter(email__iexact=email).first()
            if user:
                user.clerk_user_id = clerk_user_id
                user.save(update_fields=['clerk_user_id'])
                return user

            # Create new user
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

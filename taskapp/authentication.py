from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import jwt


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = self._get_token(request)
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationFailed("Token expired") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationFailed("Invalid token") from exc

        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Invalid token payload")

        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise AuthenticationFailed("User not found")

        return (user, None)

    @staticmethod
    def _get_token(request):
        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            return header[7:].strip()

        token = request.headers.get("JWT")
        if token:
            return token.strip()

        return None

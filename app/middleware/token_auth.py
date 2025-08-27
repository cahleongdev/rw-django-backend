import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

from app.models.users import User


@database_sync_to_async
def get_user(token_key):
    try:
        # Decode the JWT token
        decoded_data = jwt.decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data.get("user_id")

        # Get the user
        return User.objects.get(id=user_id)
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            # Get the token from query string
            query_string = scope.get("query_string", b"").decode()
            query_params = dict(x.split("=") for x in query_string.split("&") if x)

            token_key = query_params.get("token", None)

            if token_key:
                scope["user"] = await get_user(token_key)
            else:
                scope["user"] = AnonymousUser()
        except:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

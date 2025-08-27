from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken


class AnalyzeTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get("Authorization", None)
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                access_token = AccessToken(token)
                request.token_data = {
                    "email": access_token.get("email"),
                    "role": access_token.get("role"),
                    "school": access_token.get("school"),
                    "agency": access_token.get("agency"),
                    "user_id": access_token.get("user_id"),
                }
            except Exception as e:
                request.token_data = {}
        else:
            request.token_data = {}

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken

import app.constants.msg as MSG_CONST


class RoleBasedAccessMiddleware(MiddlewareMixin):
    RESTRICTED_ENDPOINTS = {
        "Super_Admin": [],
        "School_Admin": [],
    }

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
        print(request.token_data)
        if request.token_data:
            role = request.token_data["role"]
            print(request.resolver_match)
            if request.resolver_match:
                view = request.resolver_match.view_name
                if (
                    role in self.RESTRICTED_ENDPOINTS
                    and view not in self.RESTRICTED_ENDPOINTS[role]
                ):
                    return JsonResponse(
                        {"error": MSG_CONST.MSG_UNAUTHORIZED_ACCESS},
                        status=403,
                    )
            else:
                # Block access if resolver_match is None and role is in restricted endpoints
                if role in self.RESTRICTED_ENDPOINTS:
                    return JsonResponse(
                        {"error": MSG_CONST.MSG_UNAUTHORIZED_ACCESS},
                        status=403,
                    )
        return None

from rest_framework_simplejwt.tokens import AccessToken


def get_user_data_from_token(token):
    decoded = AccessToken(token)
    return {
        "email": decoded.get("email"),
        "role": decoded.get("role"),
        "title": decoded.get("title"),
    }

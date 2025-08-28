# import jwt
# from datetime import datetime, timedelta, timezone
# from rest_framework import exceptions
# from rest_framework.request import Request
# from rest_framework.authentication import BaseAuthentication, get_authorization_header
# from rest_framework.exceptions import AuthenticationFailed
# from account.models import User
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Custom Authentication Class is meant to checks JWT token in the request header and verifies it.
# class JWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = get_authorization_header(request).split()
        
#         if len(auth_header) != 2:
#             raise AuthenticationFailed('Authorization header is malformed')

#         try:
#             token = auth_header[1].decode('utf-8')
#         except UnicodeDecodeError:
#             raise AuthenticationFailed('Invalid token encoding')

#         try:
#             payload = decode_access_token(token)
#             user_id = payload['user_id']
#             user = User.objects.get(pk=user_id)
#             # Optionally attach payload if needed: request.user.jwt_payload = payload
#         except User.DoesNotExist:
#             raise AuthenticationFailed('User not found')
#         except Exception as e:
#             raise AuthenticationFailed(f'Token validation error: {str(e)}')

#         return (user, None)
#                   # return (user, None)

# # JWT token has three parts (Header.Payload.Signature).

import jwt
from datetime import datetime, timedelta, timezone
from account.models import User
import os

def create_access_token(user: User):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=2400),    # Access token expires in 40 minutes
    }
    secret = os.getenv('JWT_SECRET_KEY', 'default_secret')
    return jwt.encode(payload, secret, algorithm='HS256')

def decode_access_token(token):
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_secret')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def create_refresh_token(user: User):
    payload = {
        'user_id': user.id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
    }
    secret = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
    return jwt.encode(payload, secret, algorithm='HS256')

def decode_refresh_token(token):
    try:
        secret = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
        return jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token expired")
    except jwt.DecodeError:
        raise ValueError("Invalid refresh token")



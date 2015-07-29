from social.utils import handle_http_errors
from social.backends.open_id import OpenIdAuth, OpenIdConnectAuth
from social.backends.oauth import BaseOAuth2, BaseOAuth1
from social.exceptions import AuthMissingParameter
from social.backends.google import *

class GoogleFitOAuth2(BaseGoogleOAuth2API, BaseOAuth2):
    """Google Fit OAuth2 authentication backend"""
    name = 'google-fit'
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
    ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/revoke'
    REVOKE_TOKEN_METHOD = 'GET'
    # The order of the default scope is important
    DEFAULT_SCOPE = ['email', 
	'https://www.googleapis.com/auth/fitness.activity.read',
	'https://www.googleapis.com/auth/fitness.location.read'
	]
    DEPRECATED_DEFAULT_SCOPE = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token', True),
        ('expires_in', 'expires'),
        ('token_type', 'token_type', True)
    ]

    
    
    """"# The order of the default scope is important
    DEFAULT_SCOPE = ['openid', 'email', 'profile']
    DEPRECATED_DEFAULT_SCOPE = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    """
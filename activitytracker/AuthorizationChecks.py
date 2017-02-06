import requests
from requests_oauthlib import OAuth1
from social.apps.django_app.default.models import *
from activitytracker.models import *
from config import *
from django.http import HttpResponse, HttpResponseBadRequest
from datetime import datetime

EARLIEST_DATA_DATE = '2017-01-01'

ERROR_MESSAGE = 'An Error has occurred. Please refresh the page and try again'

SUCCESS_MESSAGE = " Activities have been synced"

DUMMY_LAST_UPDATED_INIT_VALUE = '0000-00-00 00:00:00'

class Validation(object):

    def __init__(self, user_social_instance):
        self.user = user_social_instance.user
        self.user_social_instance = user_social_instance
        self.metadata = user_social_instance.userextraproviderinfo
        self.provider_data = user_social_instance.extra_data
        self.provider_id = user_social_instance.uid
        self.PROVIDER = user_social_instance.provider.replace('-', '_').upper()
        self.RATE_LIMIT_CODE = 429

    def validateOAuth1Credentials(self, url, client_key, client_secret, resource_owner_key, resource_owner_secret):
        """
        validates credentials of OAuth1 type
        :param url: needed validation url
        :param client_key: the key of our app
        :param client_secret: the secret key of our app
        :param resource_owner_key: the public key of the Instagram user
        :param resource_owner_secret: the secret key of the instagram user
        :return: the status code indicating the outcome of the request. 200 means success
        """
        auth = OAuth1(client_key,
                      client_secret,
                      resource_owner_key,
                      resource_owner_secret
                      )
        return requests.get(url=url, auth=auth).status_code

    def validateOAuth2Credentials(self, url, params):
        """
        validates credentials of OAuth2 type
        :param url: the url for the token validation
        :param params: the needed validation token and data
        :return: the status code of the HTTP request. Anything else than 200 indicates error
        """
        return requests.get(url=url, params=params).status_code

    def evaluateResponse(self, verification_response, rate_limit_code, accept_code=200):
        """
        :param accept_code: the provider's code indicating a success, usually 200
        :return: a string indicating the outcome of the validation
        """
        if verification_response == accept_code:
            return 'Authentication Successful'
        elif verification_response == rate_limit_code:
            return 'Cannot Process Request'
        else:
            return 'Authentication Failed'

class OAuth1Validation(Validation):
    """
    A class that is responsible for performing an OAuth1 verification
    """
    def __init__(self, user_social_instance):
        super(OAuth1Validation, self).__init__(user_social_instance)

        self.api_validation_url = eval(self.PROVIDER + '_API_VALIDATION_URL')
        self.client_key = eval('SOCIAL_AUTH_' + self.PROVIDER + '_KEY')
        self.client_secret = eval('SOCIAL_AUTH_' + self.PROVIDER + '_SECRET')
        self.resource_owner_key = self.provider_data['access_token']['oauth_token']
        self.resource_owner_secret = self.provider_data['access_token']['oauth_token_secret']

    def validate(self):
        """
        :return: Returns the outcome of the validation of the user
        """
        response = self.validateOAuth1Credentials(self.api_validation_url,
                                                  self.client_key,
                                                  self.client_secret,
                                                  self.resource_owner_key,
                                                  self.resource_owner_secret
                                                  )
        return self.evaluateResponse(response, rate_limit_code=self.RATE_LIMIT_CODE)



class OAuth2Validation(Validation):
    """
    A class responsible for performing an OAuth2 validation
    """
    def __init__(self, user_social_instance):
        super(OAuth2Validation, self).__init__(user_social_instance)

        self.api_validation_url = eval(self.PROVIDER + '_API_VALIDATION_URL')
        self.client_key = eval('SOCIAL_AUTH_' + self.PROVIDER + '_KEY')
        self.client_secret = eval('SOCIAL_AUTH_' + self.PROVIDER + '_SECRET')
        self.resource_owner_key = self.provider_data['access_token']
        self.parameters = {'access_token': self.resource_owner_key}

    def attemptTokenRefresh(self):
        """
        A function that attempts to refresh an expired access token through the refresh
        token, only if such a token is available in the database
        :return: The outcome of the validation. Success indicates that our app
         got a new valid access token through the user of the refresh token
        """
        if 'refresh_token' in self.provider_data:

            refresh_url = eval(self.PROVIDER + '_API_REFRESH_TOKEN_URL')
            headers = {}
            refresh_parameters = {'client_id': self.client_key,
                                  'client_secret': self.client_secret,
                                  'refresh_token': self.provider_data['refresh_token'],
                                  'grant_type': 'refresh_token'
                                  }

            # Fitbit requires a specific base64-encoded Authorization header
            if self.PROVIDER == 'FITBIT':
                import base64
                headers = {
                    'Authorization': 'Basic %s' % (base64.b64encode(self.client_key + ':' + self.client_secret)),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }

            provider_response = requests.post(refresh_url, headers=headers, params=refresh_parameters).json()

            if 'error_description' not in provider_response:
                if 'refresh_token' in provider_response:
                    self.provider_data['refresh_token'] = provider_response['refresh_token']

                self.provider_data['access_token'] = provider_response['access_token']
                self.user_social_instance.save()
                return 'Authentication Successful'

        return 'Authentication Failed'

    def validate(self):
        """
        :return: The outcome of the OAuth2 validation
        """
        response = self.validateOAuth2Credentials(self.api_validation_url, self.parameters)

        answer = self.evaluateResponse(response, rate_limit_code=self.RATE_LIMIT_CODE)

        if answer != "Authentication Successful":
            return self.attemptTokenRefresh()
        else:
            return answer

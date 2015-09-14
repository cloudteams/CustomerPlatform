SERVER_URL = 'http://127.0.0.1:8000'

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_USER_MODEL = 'activitytracker.User'
SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'id']

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '%s/activitytracker/social_login/RegisteredUser' % SERVER_URL
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '%s/activitytracker/social_login/NewUser' % SERVER_URL
SOCIAL_AUTH_LOGIN_ERROR_URL = '%s/activitytracker/social_login/LoginFailed' % SERVER_URL
SOCIAL_AUTH_INACTIVE_USER_URL = '%s/activitytracker/social_login/InactiveUser' % SERVER_URL
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '%s/admin' % SERVER_URL
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

AVAILABLE_PROVIDERS = ['twitter', 'runkeeper', 'instagram', 'youtube', 'fitbit', 'foursquare', 'facebook-activity']

SOCIAL_AUTH_FACEBOOK_KEY = '949415351759446'
SOCIAL_AUTH_FACEBOOK_SECRET = '894924c4ef7cc1d80e24de8351d54ed5'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_location', 'user_birthday']
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [('gender','gender')]

SOCIAL_AUTH_FACEBOOK_ACTIVITY_KEY = '949415351759446'
SOCIAL_AUTH_FACEBOOK_ACTIVITY_SECRET = '894924c4ef7cc1d80e24de8351d54ed5'
SOCIAL_AUTH_FACEBOOK_ACTIVITY_SCOPE = [
    'email',
    'public_profile',
    'user_status',
    'user_location',
    'user_birthday',
    'user_friends',
    'user_actions.books',
    'user_actions.fitness',
    'user_actions.music'
]

SOCIAL_AUTH_RUNKEEPER_KEY = '28b5a3c586a14702b26d8f7b434739eb'
SOCIAL_AUTH_RUNKEEPER_SECRET = 'd4b3ad29cbe243b186304489eded430e'

SOCIAL_AUTH_TWITTER_KEY = 'c6YYBkHzDPfhU8skoCTSkQLP3'
SOCIAL_AUTH_TWITTER_SECRET = '9Zq9Zqx18IL63I52gFo2GTOya7abltxyhQOgJszyqFBEyQ30Pf'

SOCIAL_AUTH_INSTAGRAM_KEY = '78191e2522f5498d8e1c5f2adf7fd44f'
SOCIAL_AUTH_INSTAGRAM_SECRET = '9b0b8014f70a478bab1c5a5e31751f80'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '301844234502-qjirjlaip7bjsl8s5no2kvqnbt28qukp.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '3pzMxKrCbBbnRB8jfAhHj27e'
SOCIAL_AUTH_GOOGLE_EXTRA_DATA = [('gender','gender')]

SOCIAL_AUTH_YOUTUBE_KEY = '980120969173-50aro253oopgvn281fkrjpfkse8gu3sj.apps.googleusercontent.com'
SOCIAL_AUTH_YOUTUBE_SECRET = 'ojtUGWFkYQ8Ie_AaV04LMYau'
SOCIAL_AUTH_YOUTUBE_AUTH_EXTRA_ARGUMENTS = {
      'access_type': 'offline'
}


SOCIAL_AUTH_GMAIL_KEY = '1068146816408-o2kbmi91qq5n6j1gjh6ho7iv9rrd9g0j.apps.googleusercontent.com'
SOCIAL_AUTH_GMAIL_SECRET = 'byQg2WaM5EWHBNiWSefkQ25o'
SOCIAL_AUTH_GMAIL_AUTH_EXTRA_ARGUMENTS = {
      'access_type': 'offline'
}


SOCIAL_AUTH_FITBIT_KEY = '84d01602eb418700867059c70d961595'
SOCIAL_AUTH_FITBIT_SECRET = '98a58f4d05c3f167f1b188ecb5236af5'

SOCIAL_AUTH_FOURSQUARE_KEY = 'G34EKEHPMJNM1MHO2MR0NVODUYXWN0UCZ22TDPVMHKAIHY3A'
SOCIAL_AUTH_FOURSQUARE_SECRET = 'HFEJXWII5OTCC2QBQ1JETUPFMLXKMSWROXGB05U5DW3N05UB'

""" Needed info for the above applications """

TWITTER_API_VALIDATION_URL = 'https://api.twitter.com/1.1/account/verify_credentials.json'

RUNKEEPER_API_VALIDATION_URL = 'https://api.runkeeper.com/user'

INSTAGRAM_API_VALIDATION_URL = 'https://api.instagram.com/v1/users/self'

FACEBOOK_ACTIVITY_API_VALIDATION_URL = 'https://graph.facebook.com/me'

FITBIT_API_VALIDATION_URL = 'https://api.fitbit.com/1/user/-/profile.json'

FOURSQUARE_API_VALIDATION_URL = 'https://api.foursquare.com/v2/users/self'

YOUTUBE_API_VALIDATION_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
YOUTUBE_API_REFRESH_TOKEN_URL = 'https://www.googleapis.com/oauth2/v3/token'

GMAIL_API_VALIDATION_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GMAIL_API_REFRESH_TOKEN_URL = 'https://www.googleapis.com/oauth2/v3/token'

SOCIAL_AUTH_PIPELINE = (
    (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social.pipeline.user.create_user',

    # Update gender, birthday according to what the provider gives
    'activitytracker.pipeline.fill_extra_info',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social.pipeline.user.user_details'
)
)

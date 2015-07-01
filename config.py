SECRET_KEY = 'o2gyhpz9aodq95f#*=jj#(sb@0c&ss&07+8-p3k&97mhqcx349'
EMAIL_HOST_USER = 'Activitytracker.app@gmail.com'
EMAIL_HOST_PASSWORD = 'Activitytrackerpassword'

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_FACEBOOK_KEY = '995769567124024'
SOCIAL_AUTH_FACEBOOK_SECRET = '5e6c4fcf2e8c1cd3eb948442e85d93cf'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [('gender','gender')]
SOCIAL_AUTH_USER_MODEL = 'activitytracker.User'
SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'id']

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://127.0.0.1:8000/activitytracker/social_login/RegisteredUser'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = 'http://127.0.0.1:8000/activitytracker/social_login/NewUser'
SOCIAL_AUTH_LOGIN_ERROR_URL = 'http://127.0.0.1:8000/activitytracker/social_login/LoginFailed'
SOCIAL_AUTH_INACTIVE_USER_URL = 'http://127.0.0.1:8000/activitytracker/social_login/InactiveUser'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = 'http://127.0.0.1:8000/admin'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

SOCIAL_AUTH_RUNKEEPER_KEY = '8208f31a27664d69aa3f6e50997bd794'
SOCIAL_AUTH_RUNKEEPER_SECRET = '94f8def53dae4e88aeffb9ee2ae5dd5e'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '301844234502-qjirjlaip7bjsl8s5no2kvqnbt28qukp.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'aL2SDzyOJegL_97s3XqWVMl_'
SOCIAL_AUTH_GOOGLE_EXTRA_DATA = [('gender','gender')]



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

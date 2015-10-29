from datetime import datetime

def fill_extra_info(backend, user, response, *args, **kwargs):

    if user.gender is None:
        try:
            user.gender = response.get('gender')[:1].capitalize() or None
        except:
            pass

    birthday = response.get('birthday', None)

    if birthday and backend.name in ('google-oauth2', 'facebook'):

        if backend.name == "google-oauth2":
            birthday_parts = birthday.split('-')
            if birthday_parts[0] == '0000':
                birthday = '%s-%s-%s' % ('2000', birthday_parts[1], birthday_parts("-")[2])
        else:
            birthday_parts = birthday.split('/')
            birthday = '%s-%s-%s' % (birthday_parts[2], birthday_parts[0], birthday_parts[1])

        user.date_of_birth = birthday

    if backend.name == "facebook":
        location = response.get('location')
        user.location = location['name']

    user.save()
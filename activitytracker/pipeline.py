from datetime import datetime

def fill_extra_info(backend, user, response, *args, **kwargs):

    if user.gender is None:
        try:
            user.gender = response.get('gender')[:1].capitalize() or None
        except:
            pass

    birthday = response.get('birthday', None)

    if birthday:
        if backend.name == "google-oauth2":
            if birthday.split("-")[0] == '0000':
                birthday = '%s-%s-%s' % ('2000', birthday.split("-")[1], birthday.split("-")[2])
        else:
            birthday = birthday.replace('/', '-')

        user.date_of_birth = birthday

    if backend.name == "facebook":
        location = response.get('location')
        user.location = location['name']

    user.save()
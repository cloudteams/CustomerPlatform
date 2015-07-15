from datetime import datetime

def fill_extra_info(backend, user, response, *args, **kwargs):

    if user.gender is None:
        try:
            user.gender = response.get('gender')[:1].capitalize() or None
            user.save()
        except:
            pass

    if backend.name == 'google-oauth2':
        birthday = response.get('birthday', None)
        if birthday is not None:
            if birthday.split("-")[0] == '0000':
                birthday = str(datetime.now().year) + '-' + birthday.split("-")[1] + '-' + birthday.split("-")[2]
        if user.date_of_birth is None:
            user.date_of_birth = birthday
            user.save()

    if backend.name == "youtube":
        user
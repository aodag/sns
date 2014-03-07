from . import api


def activation_token(info, request):
    token = request.session.get('registration.token')
    if token is None:
        request.session['registration.token'] = token = request.GET.get('t')
    email = request.session.get('registration.email')
    if email is None:
        request.session['registration.email'] = email = request.GET.get('e')

    if token is None or email is None:
        return False

    return api.verify_token(request,
                            email, token)

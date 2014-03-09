from pyramid.view import view_config
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid import security
from . import schema
from . import api
from . import predicates


@view_config(route_name="top")
def index(request):
    return request.response


@view_config(route_name="register",
             renderer="register.mako")
class RegistrationFormView(FormView):
    schema = schema.RegistrationSchema()
    buttons = ('register',)

    def register_success(self, values):
        email = values['email']
        api.register(self.request, email)
        return HTTPFound(self.request.route_url('top'))


@view_config(route_name="activate",
             custom_predicates=(predicates.activation_token,),
             renderer="activate.mako")
class ActivationFormView(FormView):
    schema = schema.ActivationSchema()
    buttons = ('activate',)

    def activate_success(self, values):
        email = self.request.session['registration.email']
        user = api.activate(self.request,
                            email,
                            values['username'],
                            values['password'])
        auth = security.remember(self.request, user.username)
        response = HTTPFound(self.request.route_url('mypage'))
        response.headerlist.extend(auth)
        return response


@view_config(route_name="mypage",
             permission="view")
class MyPageView(object):
    def __init__(self, request):
        self.request = request

    def __call__(self):
        return self.request.response

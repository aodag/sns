import logging
from pyramid.view import view_config
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid import security
from . import schema
from . import api
from . import predicates

logger = logging.Logger(__name__)


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


@view_config(route_name="profile",
             permission="view")
def profile_view(request):
    return dict()


@view_config(route_name="profile",
             name="edit",
             permission="edit")
class ProfileEditForm(FormView):
    schema = schema.UserProfileSchema()
    buttons = ('save',)


@view_config(route_name="login",
             renderer="login.mako")
class LoginFormView(FormView):
    schema = schema.LoginSchema()
    buttons = ('login',)

    def login_success(self, values):
        logger.info("login {0}".format(values))
        auth = api.login(self.request,
                         values['username'],
                         values['password'])
        if auth is None:
            return

        response = HTTPFound(self.request.route_url('mypage'))
        response.headerlist.extend(auth)
        return response

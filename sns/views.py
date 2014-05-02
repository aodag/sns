import logging
from pyramid.view import view_config
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from . import schema
from . import api

logger = logging.Logger(__name__)


@view_config(route_name="top")
def index(request):
    return request.response


@view_config(route_name="mypage",
             permission="view")
class MyPageView(object):
    def __init__(self, request):
        self.request = request

    def __call__(self):
        return self.request.response


@view_config(route_name="profile",
             permission="view",
             renderer='user_profile.mako')
def profile_view(context, request):
    profile = context.profile

    if profile is None:
        raise HTTPNotFound

    return dict(profile=profile)


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

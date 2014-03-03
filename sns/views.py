from pyramid.view import view_config
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from .schema import RegistrationSchema
from . import api


@view_config(route_name="top")
def index(request):
    return request.response


@view_config(route_name="register",
             renderer="register.mako")
class RegistrationFormView(FormView):
    schema = RegistrationSchema()
    buttons = ('register',)

    def register_success(self, values):
        email = values['email']
        api.register(self.request, email)
        return HTTPFound(self.request.route_url('top'))

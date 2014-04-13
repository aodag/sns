from pyramid.view import view_config
from pyramid import security
from pyramid.httpexceptions import HTTPFound
from pyramid_deform import FormView
from sns import predicates
from sns import schema
from sns import api


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

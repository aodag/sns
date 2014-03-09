from pyramid import security
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer import get_mailer
from zope.interface import directlyProvides
from .interfaces import (
    IMessageFactory,
    IRegistration,
    ITokenGenerator,
    ITokenStore,
    IUserAuthenticator,
    IUserFactory,
)


def get_registration(request):
    reg = request.registry
    mailer = get_mailer(request)
    directlyProvides(mailer, IMailer)

    message_factory = reg.getUtility(IMessageFactory)
    token_store = reg.getUtility(ITokenStore)
    token_generator = reg.getUtility(ITokenGenerator)
    user_factory = reg.getUtility(IUserFactory)

    registration = reg.getMultiAdapter(
        [mailer, message_factory,
         token_store, token_generator, user_factory],
        IRegistration)
    return registration


def register(request, email):
    registration = get_registration(request)
    return registration.register(email)


def verify_token(request, email, token):
    registration = get_registration(request)
    return registration.verify_token(email, token)


def activate(request, email, username, password):
    registration = get_registration(request)
    return registration.activate(email, username, password)


def login(request, username, password):
    authenticator = request.registry.getUtility(IUserAuthenticator)
    auth = authenticator(username, password)
    if not auth:
        return None
    return security.remember(request, auth)

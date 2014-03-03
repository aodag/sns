from pyramid_mailer.interfaces import IMailer
from pyramid_mailer import get_mailer
from zope.interface import directlyProvides
from .interfaces import (
    IMessageFactory,
    IRegistration,
    ITokenGenerator,
    ITokenStore,
)


def register(request, email):
    reg = request.registry
    mailer = get_mailer(request)
    directlyProvides(mailer, IMailer)

    message_factory = reg.getUtility(IMessageFactory)
    token_store = reg.getUtility(ITokenStore)
    token_generator = reg.getUtility(ITokenGenerator)

    registration = reg.getMultiAdapter(
        [mailer, message_factory,
         token_store, token_generator], IRegistration)
    return registration.register(email)

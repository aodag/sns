import logging
import uuid
from zope.interface import implementer, directlyProvides
from pyramid import renderers
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.message import Message
from pyramid_mako import add_mako_renderer
from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE
from .interfaces import (
    IMessageFactory,
    IRegistration,
    ITokenGenerator,
    ITokenStore,
    IUserFactory
)
from .models import DBSession, User


logger = logging.getLogger(__name__)


def includeme(config):
    add_mako_renderer(config, '.txt')
    reg = config.registry
    region = make_region()
    region.configure_from_config(config.registry.settings,
                                 'cache.registration.')
    store = DogPileTokenStore(region)
    message_factory = RegistrationMessageFactory(
        sender=config.registry.settings['registration.mail.sender'])

    reg.utilities.register([], ITokenStore,
                           "",
                           store)
    reg.utilities.register([], ITokenGenerator,
                           "",
                           generate_uuid_token)
    reg.utilities.register([], IMessageFactory,
                           "",
                           message_factory)
    reg.utilities.register([], IUserFactory,
                           "",
                           user_factory)
    reg.adapters.register([IMailer, IMessageFactory,
                           ITokenStore, ITokenGenerator,
                           IUserFactory,
                           ],
                          IRegistration,
                          "",
                          Registration)


def user_factory(email, username, password):
    user = User(email=email, username=username, password=password)
    DBSession.add(user)
    return user

directlyProvides(user_factory, IUserFactory)


@implementer(IMessageFactory)
class RegistrationMessageFactory(object):
    def __init__(self, sender):
        self.sender = sender

    def __call__(self, email, token):
        body = renderers.render(
            'sns:templates/mail/registration#body.txt',
            dict(email=email,
                 token=token))

        subject = renderers.render(
            'sns:templates/mail/registration#subject.txt',
            dict(email=email,
                 token=token))

        return Message(recipients=[email],
                       body=body,
                       sender=self.sender,
                       subject=subject.strip())


@implementer(ITokenStore)
class DogPileTokenStore(object):
    def __init__(self, region):
        self.region = region

    def __getitem__(self, key):
        v = self.region.get(key)
        if v == NO_VALUE:
            raise KeyError(key)
        return v

    def __setitem__(self, key, value):
        print("{0}:{1}".format(key, value))
        logger.info('token store put {0}:{1}'.format(key, value))
        self.region.set(key, value)
        print("{0}".format(self.region.backend))

    def __delitem__(self, key):
        self.region.delete(key)

    def __contains__(self, key):
        return self.region.get(key) != NO_VALUE


def generate_uuid_token():
    return uuid.uuid4().hex

directlyProvides(generate_uuid_token, ITokenGenerator)


@implementer(IRegistration)
class Registration(object):
    def __init__(self, mailer, message_factory,
                 token_store, token_generator, user_factory):
        self.mailer = mailer
        self.message_factory = message_factory
        self.token_store = token_store
        self.token_generator = token_generator
        self.user_factory = user_factory

    def register(self, email):
        logger.debug('register {0}'.format(email))
        token = self.token_generator()
        self.token_store[email] = token
        message = self.message_factory(email, token)
        self.mailer.send(message)

    def verify_token(self, email, token):
        if email not in self.token_store:
            return False

        return self.token_store[email] == token

    def activate(self, email, username, password):
        del self.token_store[email]
        user = self.user_factory(email, username, password)
        return user

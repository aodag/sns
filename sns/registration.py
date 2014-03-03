import uuid
from zope.interface import implementer, directlyProvides
from pyramid import renderers
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.message import Message
from pyramid_mako import add_mako_renderer
from dogpile.cache import make_region
from .interfaces import (
    IMessageFactory,
    IRegistration,
    ITokenGenerator,
    ITokenStore,
)


def includeme(config):
    add_mako_renderer(config, '.txt')
    reg = config.registry
    region = make_region().configure(
        'dogpile.cache.memory'
    )
    store = DogPileTokenStore(region)
    message_factory = RegistrationMessageFactory()

    reg.utilities.register([], ITokenStore,
                           "",
                           store)
    reg.utilities.register([], ITokenGenerator,
                           "",
                           generate_uuid_token)
    reg.utilities.register([], IMessageFactory,
                           "",
                           message_factory)
    reg.adapters.register([IMailer, IMessageFactory,
                           ITokenStore, ITokenGenerator],
                          IRegistration,
                          "",
                          Registration)


@implementer(IMessageFactory)
class RegistrationMessageFactory(object):
    def __init__(self):
        pass

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
                       subject=subject.strip())


@implementer(ITokenStore)
class DogPileTokenStore(object):
    def __init__(self, region):
        self.region = region

    def __getitem__(self, key):
        return self.region.get(key)

    def __setitem__(self, key, value):
        self.region.set(key, value)

    def __delitem__(self, key):
        self.region.delete(key)


def generate_uuid_token():
    return uuid.uuid4().hex

directlyProvides(generate_uuid_token, ITokenGenerator)


@implementer(IRegistration)
class Registration(object):
    def __init__(self, mailer, message_factory, token_store, token_generator):
        self.mailer = mailer
        self.message_factory = message_factory
        self.token_store = token_store
        self.token_generator = token_generator

    def register(self, email):
        token = self.token_generator()
        self.token_store[email] = token
        message = self.message_factory(email, token)
        self.mailer.send(message)

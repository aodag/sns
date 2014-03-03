from zope.interface import Interface, Attribute
from pyramid.interfaces import IDict


class IRegistration(Interface):
    mailer = Attribute(u"A mailer for notify token")
    message_factory = Attribute(u"Creating mail message")
    token_store = Attribute(u"A store for keep token")
    token_generator = Attribute(u"generating token for registration")

    def register(email):
        """ invoke registration procedure """


class ITokenGenerator(Interface):
    def __call__():
        """ generate token """


class ITokenStore(IDict):
    """ token store is IDict interface """


class IMessageFactory(Interface):
    """ message factory"""

    def __call__(email, token):
        """ create message """

import unittest
from zope.interface.verify import verifyObject
from testfixtures import compare, Comparison as C


class TestRegistration(unittest.TestCase):

    def _getTarget(self):
        from ..registration import Registration
        return Registration

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_iface(self):
        from ..interfaces import IRegistration
        target = self._makeOne(None, None, None, None)
        verifyObject(IRegistration, target)

    def test_register(self):
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        email = "sns@example.com"

        mailer = DummyMailer()
        message_factory = lambda email, token: Message(recipients=[email])
        token_store = dict()
        token_generator = lambda: "this-is-testing-token"
        target = self._makeOne(mailer, message_factory,
                               token_store, token_generator)
        target.register(email)

        assert email in target.token_store
        assert target.token_store[email] == 'this-is-testing-token'

        compare(target.mailer.outbox[0],
                C(Message,
                  recipients=[email],
                  strict=False))

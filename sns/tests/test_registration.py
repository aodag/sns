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
        target = self._makeOne(None, None, None, None, None)
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
                               token_store, token_generator,
                               None,)
        target.register(email)

        assert email in target.token_store
        assert target.token_store[email] == 'this-is-testing-token'

        compare(target.mailer.outbox[0],
                C(Message,
                  recipients=[email],
                  strict=False))

    def test_verify_token(self):
        email = "sns@example.com"

        token = "this-is-testing-token"
        token_store = {email: token}
        target = self._makeOne(None, None,
                               token_store, None,
                               None)

        assert target.verify_token(email, token)

    def test_verify_token_empty(self):
        email = "sns@example.com"

        token = "this-is-testing-token"
        token_store = {}
        target = self._makeOne(None, None,
                               token_store, None,
                               None)

        assert not target.verify_token(email, token)

    def test_verify_token_invalid(self):
        email = "sns@example.com"

        token = "this-is-testing-token"
        token_store = {email: token + "x"}
        target = self._makeOne(None, None,
                               token_store, None,
                               None)

        assert not target.verify_token(email, token)

    def test_activate(self):
        username = "user1"
        email = "user@example.com"
        password = "secret-password"

        token = "this-is-testing-token"
        token_store = {email: token}
        target = self._makeOne(None, None,
                               token_store, None,
                               lambda email, username, password:
                               (email, username, password))

        result = target.activate(email, username, password)

        compare(result, (email, username, password))
        compare(token_store, {})

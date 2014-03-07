import unittest
from testfixtures import ShouldRaise


class TestUser(unittest.TestCase):

    def _getTarget(self):
        from ..models import User
        return User

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_verify_password(self):
        user = self._makeOne()
        user.password = 'password'

        with ShouldRaise(AttributeError):
            user.password == 'password'

        self.assertTrue(user.verify_password('password'))

    def test_verify_password_invalid(self):
        user = self._makeOne()
        user.password = 'password'
        self.assertFalse(user.verify_password('xpassword'))

    def test_hash(self):
        user = self._makeOne()
        self.assertEqual(len(user._hash('')), 40)
        self.assertEqual(len(user._hash('*' * 100)), 40)

import unittest
from testfixtures import ShouldRaise, compare


class TestUser(unittest.TestCase):

    def _getTarget(self):
        from ..models import User
        return User

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeProfile(self, *args, **kwargs):
        from ..models import UserProfile
        return UserProfile(*args, **kwargs)

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
        compare(len(user._hash('')), 40)
        compare(len(user._hash('*' * 100)), 40)

    def test_has_profile_no_profile(self):
        user = self._makeOne()
        result = user.has_profile()
        self.assertFalse(result)

    def test_has_profile(self):
        user = self._makeOne()
        self._makeProfile(user=user)

        result = user.has_profile()
        self.assertTrue(result)

    def test_new_profile(self):
        user = self._makeOne()
        result = user.new_profile()
        compare(result.user, user)

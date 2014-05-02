import unittest
from testfixtures import compare, Comparison as C
from pyramid import testing


def setUpModule():
    from sqlalchemy import create_engine
    from ..models import init
    engine = create_engine('sqlite:///')
    init(engine, create=True)


def tearDownModule():
    import transaction
    transaction.abort()


class TestProfileResource(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from ..resources import ProfileResource
        return ProfileResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeUser(self, *args, **kwargs):
        from ..models import User, DBSession
        user = User(*args, **kwargs)
        DBSession.add(user)
        return user

    def _makeUserProfile(self, *args, **kwargs):
        from ..models import UserProfile, DBSession
        profile = UserProfile(*args, **kwargs)
        DBSession.add(profile)
        return profile

    def test_username(self):
        request = testing.DummyRequest(
            matchdict={'username': 'testing-user'})
        target = self._makeOne(request)

        result = target.username

        compare(result, "testing-user")

    def test_profile_empty(self):

        request = testing.DummyRequest(
            matchdict={'username': 'testing-user'})
        target = self._makeOne(request)

        result = target.profile

        compare(result, None)

    def test_profile(self):
        user = self._makeUser(username='testing-user')
        profile = self._makeUserProfile(user=user)

        request = testing.DummyRequest(
            matchdict={'username': 'testing-user'})
        target = self._makeOne(request)

        result = target.profile

        compare(result, C(type(profile), user=user, strict=False))

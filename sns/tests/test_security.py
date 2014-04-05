import unittest
from testfixtures import compare
from pyramid import testing


def setUpModule():
    from sqlalchemy import create_engine
    from sns import models
    engine = create_engine('sqlite:///')
    models.init(engine, create=True)

def tearDownModle():
    import transaction
    from sns import models

    transaction.abort()
    models.DBSession.remove()


class Testget_authenticated_user(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from ..security import get_authenticated_user
        return get_authenticated_user(*args, **kwargs)

    def _makeUser(self, *args, **kwargs):
        from ..models import User, DBSession
        user = User(*args, **kwargs)
        DBSession.add(user)
        return user

    def test_no_userid(self):
        request = testing.DummyRequest()
        result = self._callFUT(request)

        compare(result, None)

    def test_no_user(self):
        config = testing.setUp()
        try:
            config.testing_securitypolicy(userid='no_user')
            request = testing.DummyRequest()

            result = self._callFUT(request)

            compare(result, None)
        finally:
            testing.tearDown()

    def test_user(self):
        config = testing.setUp()
        try:
            username = 'testing_user'
            user = self._makeUser(username=username)
            config.testing_securitypolicy(userid=username)
            request = testing.DummyRequest()

            result = self._callFUT(request)

            compare(result, user)
        finally:
            testing.tearDown()

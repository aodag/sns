from pyramid.decorator import reify
from pyramid.security import Allow, Authenticated
from .models import User, UserProfile


class MyPageResource(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
        ]

    def __init__(self, request):
        self.request = request


class ProfileResource(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
        ]

    def __init__(self, request):
        self.request = request

    @reify
    def username(self):
        return self.request.matchdict.get('username')

    @reify
    def profile(self):
        if self.username is None:
            return None

        return UserProfile.query.filter(
            User.username == self.username,
            UserProfile.user_id == User.id
        ).first()

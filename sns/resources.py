from pyramid.security import Allow, Authenticated

class MyPageResource(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
        ]

    def __init__(self, request):
        self.request = request

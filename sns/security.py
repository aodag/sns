import logging
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import authenticated_userid
from .interfaces import IUserAuthenticator
from .models import User

logger = logging.getLogger(__name__)


def includeme(config):
    reg = config.registry
    authn_policy = SessionAuthenticationPolicy()
    authz_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    reg.registerUtility(authenticate_user,
                        IUserAuthenticator)

    config.add_request_method(get_authenticated_user,
                              name='authenticated_user',
                              property=True,
                              reify=True)


def authenticate_user(username, password):
    user = User.query.filter(User.username == username).first()
    if user is None:
        logger.debug('user "{0}" not found'.format(username))
        return None

    if not user.verify_password(password):
        logger.debug('user "{0}" is not verified'.format(username))
        return None

    return user.username


def get_authenticated_user(request):
    username = authenticated_userid(request)
    if not username:
        return

    return User.query.filter(User.username == username).first()

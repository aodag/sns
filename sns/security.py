import logging
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
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


def authenticate_user(username, password):
    user = User.query.filter(User.username==username).first()
    if user is None:
        logger.debug('user "{0}" not found'.format(username))
        return None

    if not user.verify_password(password):
        logger.debug('user "{0}" is not verified'.format(username))
        return None

    return user.username

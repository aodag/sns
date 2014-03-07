#
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
my_session_factory = SignedCookieSessionFactory('itsaseekreet')


def includeme(config):
    config.add_route("top", "/")
    config.add_route("register", "/register")
    config.add_route("activate", "/activate")


def main(global_conf, **settings):
    config = Configurator(settings=settings)
    config.set_session_factory(my_session_factory)
    config.include("pyramid_mako")
    config.include(".")
    config.include(".registration")
    config.scan(".views")
    return config.make_wsgi_app()

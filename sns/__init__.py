#
import os
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.session import SignedCookieSessionFactory
from . import models
my_session_factory = SignedCookieSessionFactory('itsaseekreet')


def includeme(config):
    config.add_route("top", "/")
    config.add_route("register", "/register")
    config.add_route("activate", "/activate")


def signed_cookie_session(config):
    config.set_session_factory(my_session_factory)


def main(global_conf, **settings):
    engine = engine_from_config(settings)
    models.init(engine, create=os.getenv('SNS_CREATE_TABLES'))

    config = Configurator(settings=settings)
    config.include("pyramid_mako")
    config.include("pyramid_tm")
    config.include(".")
    config.include(".registration")
    config.scan(".views")
    return config.make_wsgi_app()

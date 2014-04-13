#
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.session import SignedCookieSessionFactory
from . import models
my_session_factory = SignedCookieSessionFactory('itsaseekreet')


def includeme(config):
    config.add_route("top", "/")
    config.add_route("register", "/register")
    config.add_route("login", "/login")
    config.add_route("activate", "/activate")
    config.add_route("mypage", "/mypage",
                     factory=".resources.MyPageResource")
    config.add_route("profile", "/mypage/profile/*traversal",
                     factory=".resources.ProfileResource")


def signed_cookie_session(config):
    config.set_session_factory(my_session_factory)


def main(global_conf, **settings):
    engine = engine_from_config(settings)
    models.init(engine)

    config = Configurator(settings=settings)
    config.include("pyramid_mako")
    config.include("pyramid_layout")
    config.include("pyramid_tm")
    config.include("pyramid_deform")
    config.include(".")
    config.include(".registration")
    config.include(".security")
    config.include(".web.registration")
    config.scan(".views")
    config.scan(".layouts")
    return config.make_wsgi_app()

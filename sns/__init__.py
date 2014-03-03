#
from pyramid.config import Configurator


def includeme(config):
    config.add_route("top", "/")
    config.add_route("register", "/register")


def main(global_conf, **settings):
    config = Configurator(settings=settings)
    config.include("pyramid_mako")
    config.include(".")
    config.include(".registration")
    config.scan(".views")
    return config.make_wsgi_app()

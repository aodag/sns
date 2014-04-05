# -*- coding:utf-8 -*-

import unittest
import webtest
from testfixtures import TempDirectory


settings = {
    "pyramid.includes": ['pyramid_mailer.testing',
                         ],
    "redis.sessions.secret": "secret",
    "mako.directories": "sns:templates",
    #"cache.registration.backend": "dogpile.cache.redis",
}


def setUpModule():
    """ """
    import os
    d = TempDirectory()
    if os.getenv('SQLALCHEMY_URL'):
        settings['sqlalchemy.url'] = os.getenv('SQLALCHEMY_URL')
    else:
        sqlalchemy_url = "sqlite:///%(here)s/sns.sqlite" % dict(here=d.path)
        settings['sqlalchemy.url'] = sqlalchemy_url
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option('sqlalchemy.url', sqlalchemy_url)
        command.upgrade(alembic_cfg, "head")

    if os.getenv('USE_REDIS'):
        settings['cache.registration.backend'] = 'dogpile.cache.redis'
        settings['pyramid.includes'].append('pyramid_redis_sessions')
    else:
        from sns.testing import FakeLock
        settings['cache.registration.backend'] = "dogpile.cache.dbm"
        settings['cache.registration.arguments.filename'] = d.getpath('registration.dbm')
        settings['cache.registration.arguments.lock_factory'] = FakeLock
        settings['pyramid.includes'].append('sns.signed_cookie_session')


def tearDownModule():
    """ """
    TempDirectory.cleanup_all()


class TestSNS(unittest.TestCase):
    #settings = settings

    def _makeApp(self, **settings):
        from sns import main
        return main({}, **settings)

    def test_index(self):
        app = self._makeApp(**settings)
        app = webtest.TestApp(app)

        app.get('/')

    def test_registration(self):
        import urllib.parse
        from dogpile.cache import make_region
        tokens = make_region()
        tokens.configure_from_config(settings, 'cache.registration.')
        app = self._makeApp(**settings)

        app = webtest.TestApp(app)

        res = app.get('/register')
        email = 'sns@example.com'
        res.form['email'] = email
        res = res.form.submit('register')

        token = tokens.get(email)
        assert res.location == 'http://localhost/'
        params = {'t': token,
                  'e': email}
        res = app.get('/activate?' + urllib.parse.urlencode(params))
        res.form['username'] = 'test1'
        res.form['password'] = 'secret'
        res = res.form.submit('activate')
        assert res.location == 'http://localhost/mypage'

        app.get(res.location)

    def _makeUser(self, *args, **kwargs):
        from sqlalchemy import engine_from_config
        from sqlalchemy.orm import sessionmaker
        from sns.models import User
        engine = engine_from_config(settings)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(User(*args, **kwargs))
        session.commit()
        session.close()

    def test_login(self):
        app = self._makeApp(**settings)
        app = webtest.TestApp(app)
        username = "profile_test_user"
        email = "profile_test_user@example.com"
        password = "secret"
        self._makeUser(username=username,
                       email=email,
                       password=password)
        res = app.get('/login')
        res.form['username'] = username
        res.form['password'] = password
        res = res.form.submit('login')

        assert res.location == 'http://localhost/mypage'

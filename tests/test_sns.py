# -*- coding:utf-8 -*-

import unittest
import webtest
from testfixtures import TempDirectory


settings = {
    "pyramid.includes": ['pyramid_mailer.testing',
                         ],
    "redis.sessions.secret": "secret",
    "mako.directories": "sns:templates",
    "registration.mail.sender": "sender@example.com",
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
        user = User(*args, **kwargs)
        session.add(user)
        session.flush()
        user_id = user.id
        session.commit()
        session.close()
        return user_id

    def _makeProfile(self, *args, **kwargs):
        from sqlalchemy import engine_from_config
        from sqlalchemy.orm import sessionmaker
        from sns.models import UserProfile
        engine = engine_from_config(settings)
        Session = sessionmaker(bind=engine)
        session = Session()
        profile = UserProfile(*args, **kwargs)
        session.add(profile)
        session.flush()
        profile_id = profile.id
        session.commit()
        session.close()
        return profile_id

    def test_login(self):
        app = self._makeApp(**settings)
        app = webtest.TestApp(app)
        username = "login_user"
        email = "login_user@example.com"
        password = "secret"
        res = self._login(app, username, email, password)

        assert res.location == 'http://localhost/mypage'

    def _login(self, app, username, email, password):
        self._makeUser(username=username,
                       email=email,
                       password=password)
        res = app.get('/login')
        res.form['username'] = username
        res.form['password'] = password
        res = res.form.submit('login')
        return res

    def test_profile_forbidden(self):
        app = self._makeApp(**settings)
        app = webtest.TestApp(app)
        res = app.get('/users/no-one', status=403)

    def test_profile_no_one(self):
        app = self._makeApp(**settings)
        app = webtest.TestApp(app)
        username = "profile_no_one"
        email = "profile_no_one@example.com"
        password = "secret"
        self._login(app, username, email, password)
        res = app.get('/users/no-one', status=404)

    def test_profile(self):
        app = self._makeApp(**settings)
        app = webtest.TestApp(app)
        username = "profile"
        email = "profile@example.com"
        password = "secret"
        other_user_id = self._makeUser(
            username='profile-other',
            email='profile-other@example.com',
            password='secret')
        self._makeProfile(user_id=other_user_id)
        self._login(app, username, email, password)
        res = app.get('/users/profile-other')

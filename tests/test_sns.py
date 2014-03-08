# -*- coding:utf-8 -*-

import unittest
import webtest


settings = {
    "mako.directories": "sns:templates",
    "cache.registration.backend": "dogpile.cache.redis",
    #"sqlalchemy.url": "postgresql+psycopg2://postgres@localhost/sns_test",
    #"sqlalchemy.url": "sqlite:///",
}


def setUpModule():
    """ """
    import os
    if os.getenv('SQLALCHEMY_URL'):
        settings['sqlalchemy.url'] = os.getenv('SQLALCHEMY_URL')
    else:
        settings['sqlalchemy.url'] = "sqlite:///"
    os.environ['SNS_CREATE_TABLES'] = "1"


def tearDownModule():
    """ """


class TestSNS(unittest.TestCase):
    settings = settings

    def _makeApp(self, **settings):
        from sns import main
        return main({}, **settings)

    def test_index(self):
        app = self._makeApp(**self.settings)
        app = webtest.TestApp(app)

        app.get('/')

    def test_registration(self):
        import urllib.parse
        from dogpile.cache import make_region
        settings = self.settings.copy()
        settings.update({
            "cache.registration.backend": "dogpile.cache.redis",
        })
        tokens = make_region()
        tokens.configure_from_config(settings, 'cache.registration.')
        settings['pyramid.includes'] = ['pyramid_mailer.testing']
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

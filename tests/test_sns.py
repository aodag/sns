# -*- coding:utf-8 -*-

import unittest
import webtest
from testfixtures import tempdir


class TestSNS(unittest.TestCase):
    settings = {
        "mako.directories": "sns:templates",
    }

    def _makeApp(self, **settings):
        from sns import main
        return main({}, **settings)

    def test_index(self):
        app = self._makeApp(**self.settings)
        app = webtest.TestApp(app)

        app.get('/')

    def test_registration(self):
        settings = {}
        settings.update(self.settings)
        settings['pyramid.includes'] = ['pyramid_mailer.testing']
        app = self._makeApp(**settings)

        app = webtest.TestApp(app)

        res = app.get('/register')

        res.form['email'] = 'sns@example.com'
        res = res.form.submit('register')

        assert res.location == 'http://localhost/'

# -*- coding:utf-8 -*-
from pyramid_layout.layout import layout_config


@layout_config(template="base.mako")
class BaseLayout(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

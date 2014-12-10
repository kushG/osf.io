# -*- coding: utf-8 -*-
"""Drive addon routes."""
from framework.routing import Rule, json_renderer

from website.addons.googledrive import views
from website.routes import OsfWebRenderer, notemplate

auth_routes = {
    'rules' : [
        Rule(
            '/settings/drive-creds',
            'get',
            views.auth.drive_credentials,
            json_renderer,

        )
    ]

}
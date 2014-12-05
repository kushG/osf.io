# -*- coding: utf-8 -*-import httplib as http

import settings
import httplib as http
from framework.exceptions import HTTPError
from framework.sessions import session
from framework.status import push_status_message as flash

from flask import request
from framework.flask import redirect  # VOL-aware redirect
from framework.auth.core import _get_current_user
from website.project.decorators import (must_be_valid_project,
    must_have_addon, must_have_permission, must_not_be_registration,
)
from website.project.model import Node
from framework.auth.decorators import must_be_logged_in
from website.util import web_url_for
from website.util import api_url_for
from website.addons.gdrive.utils import serialize_settings, serialize_urls

# TODO
@must_be_valid_project
@must_have_addon('gdrive', 'node')
def gdrive_config_get(node_addon, **kwargs):
    """API that returns the serialized node settings."""
    user = _get_current_user()
    return {
        'result': serialize_settings(node_addon, user),
    }, http.OK

    
@must_have_permission('write')
@must_not_be_registration
@must_have_addon('gdrive', 'node')
def gdrive_config_put(node_addon, auth, **kwargs):
    """View for changing a node's linked gdrive folder."""
    # folder = request.json.get('selected')
    # path = folder['path']
    # node_addon.set_folder(path, auth=auth)
    node_addon.save()
    return {
        'result': {

            'urls': serialize_urls(node_addon)
        },
        'message': 'Successfully updated settings.',
    }, http.OK


@must_have_permission('write')
@must_have_addon('gdrive', 'node')
def gdrive_deauthorize(auth, node_addon, **kwargs):
    node_addon.deauthorize(auth=auth)
    node_addon.save()
    return None


@must_have_permission('write')
@must_have_addon('gdrive', 'node')
def gdrive_import_user_auth(auth, node_addon, **kwargs):
    """Import gdrive credentials from the currently logged-in user to a node.
    """
    user = auth.user
    user_addon = user.get_addon('gdrive')
    if user_addon is None or node_addon is None:
        raise HTTPError(http.BAD_REQUEST)
    node_addon.set_user_auth(user_addon)
    node_addon.save()
    return {
        'result': serialize_settings(node_addon, user),
        'message': 'Successfully imported access token from profile.',
    }, http.OK

@must_be_logged_in
def drive_auth(auth, **kwargs):
    """View function for getting access_token from javascript & saving
     in AddonGdriveUserSettings' access_token """
    user = auth.user
    # Store the node ID on the session in order to get the correct redirect URL
    # upon finishing the flow
    nid = kwargs.get('nid') or kwargs.get('pid')
    if nid:
        session.data['gdrive_auth_nid'] = nid
    if not user:
        raise HTTPError(http.FORBIDDEN)
    # If user has already authorized dropbox, flash error message
    if user.has_addon('gdrive') and user.get_addon('gdrive').has_auth:
        flash('You have already authorized Google Drive for this account', 'warning')
        return redirect(web_url_for('user_addons'))
    access_token = request.json.get('access_token')
    user.add_addon('gdrive')
    user.save()
    user_settings = user.get_addon('gdrive')
    user_settings.access_token = access_token
    user_settings.owner = user
    user_settings.save()
    node = Node.load(session.data.get('gdrive_auth_nid'))
    flash('Successfully authorized Google Drive', 'success')
    if node:
        del session.data['gdrive_auth_nid']
        # Automatically use newly-created auth
        if node.has_addon('gdrive'):
            node_addon = node.get_addon('gdrive')
            node_addon.set_user_auth(user_settings)
            node_addon.save()


@must_be_logged_in
@must_have_addon('gdrive', 'user')
def drive_auth_delete_user(user_addon, auth, **kwargs):
    user_addon.clear()
    user_addon.save()


@must_be_logged_in
@must_have_addon('gdrive', 'user')
def drive_user_config_get(user_addon, auth, **kwargs):
    """View for getting a JSON representation of the logged-in user's
    GDrive user settings.
    """
    urls = {
        'create': api_url_for('drive_auth_user'),
        'delete': api_url_for('drive_auth_delete_user'),
    }
    # info = user_addon.dropbox_info
    # valid_credentials = True

    # if user_addon.has_auth:
    #     try:
    #         client = get_client_from_user_settings(user_addon)
    #         client.account_info()
    #     except ErrorResponse as error:
    #         if error.status == 401:
    #             valid_credentials = False
    #         else:
    #             HTTPError(http.BAD_REQUEST)

    return {
        'result': {
            'userHasAuth': user_addon.has_auth,
            'client' : settings.CLIENT_ID,
            'api_key' : settings.API_KEY,
            'scope' : settings.OAUTH_SCOPE,
            'urls': urls
        },
    }, http.OK
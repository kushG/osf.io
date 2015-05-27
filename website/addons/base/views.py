# -*- coding: utf-8 -*-

import os
import json
import codecs
import httplib
import functools

import furl
from flask import request
from flask import redirect
from flask import make_response
from modularodm.exceptions import NoResultsFound

from framework.auth import Auth
from framework.sessions import session
from framework.sentry import log_exception
from framework.exceptions import HTTPError
from framework.render.tasks import build_rendered_html
from framework.auth.decorators import must_be_logged_in, must_be_signed

from website import mails
from website import settings
from website.project import decorators
from website.addons.base import exceptions
from website.models import User, Node, NodeLog
from website.util import rubeus
from website.project.utils import serialize_node
from website.project.decorators import must_be_valid_project, must_be_contributor_or_public


@decorators.must_have_permission('write')
@decorators.must_not_be_registration
def disable_addon(auth, **kwargs):
    node = kwargs['node'] or kwargs['project']

    addon_name = kwargs.get('addon')
    if addon_name is None:
        raise HTTPError(httplib.BAD_REQUEST)

    deleted = node.delete_addon(addon_name, auth)

    return {'deleted': deleted}


@must_be_logged_in
def get_addon_user_config(**kwargs):

    user = kwargs['auth'].user

    addon_name = kwargs.get('addon')
    if addon_name is None:
        raise HTTPError(httplib.BAD_REQUEST)

    addon = user.get_addon(addon_name)
    if addon is None:
        raise HTTPError(httplib.BAD_REQUEST)

    return addon.to_json(user)


def check_file_guid(guid):

    guid_url = '/{0}/'.format(guid._id)
    if not request.path.startswith(guid_url):
        url_split = request.url.split(guid.file_url)
        try:
            guid_url += url_split[1].lstrip('/')
        except IndexError:
            pass
        return guid_url
    return None

permission_map = {
    'create_folder': 'write',
    'revisions': 'read',
    'metadata': 'read',
    'download': 'read',
    'upload': 'write',
    'delete': 'write',
    'copy': 'write',
    'move': 'write',
    'copyto': 'write',
    'moveto': 'write',
    'copyfrom': 'read',
    'movefrom': 'write',
}


def check_access(node, user, action, key=None):
    """Verify that user can perform requested action on resource. Raise appropriate
    error code if action cannot proceed.
    """
    permission = permission_map.get(action, None)
    if permission is None:
        raise HTTPError(httplib.BAD_REQUEST)
    if node.has_permission(user, permission):
        return True
    if permission == 'read':
        if node.is_public or key in node.private_link_keys_active:
            return True
    code = httplib.FORBIDDEN if user else httplib.UNAUTHORIZED
    raise HTTPError(code)


def make_auth(user):
    if user is not None:
        return {
            'id': user._id,
            'email': '{}@osf.io'.format(user._id),
            'name': user.fullname,
        }
    return {}


def restrict_addrs(*addrs):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            remote = request.remote_addr
            if remote not in addrs:
                raise HTTPError(httplib.FORBIDDEN)
            return func(*args, **kwargs)
        return wrapped
    return wrapper


restrict_waterbutler = restrict_addrs(*settings.WATERBUTLER_ADDRS)


@restrict_waterbutler
def get_auth(**kwargs):
    try:
        action = request.args['action']
        node_id = request.args['nid']
        provider_name = request.args['provider']
    except KeyError:
        raise HTTPError(httplib.BAD_REQUEST)

    cookie = request.args.get('cookie')
    view_only = request.args.get('view_only')

    if 'auth_user_id' in session.data:
        user = User.load(session.data['auth_user_id'])
    elif cookie:
        user = User.from_cookie(cookie)
    else:
        user = None

    node = Node.load(node_id)
    if not node:
        raise HTTPError(httplib.NOT_FOUND)

    check_access(node, user, action, key=view_only)

    provider_settings = node.get_addon(provider_name)
    if not provider_settings:
        raise HTTPError(httplib.BAD_REQUEST)

    try:
        credentials = provider_settings.serialize_waterbutler_credentials()
        settings = provider_settings.serialize_waterbutler_settings()
    except exceptions.AddonError:
        log_exception()
        raise HTTPError(httplib.BAD_REQUEST)

    return {
        'auth': make_auth(user),
        'credentials': credentials,
        'settings': settings,
        'callback_url': node.api_url_for(
            'create_waterbutler_log',
            _absolute=True,
        ),
    }


LOG_ACTION_MAP = {
    'move': NodeLog.FILE_MOVED,
    'copy': NodeLog.FILE_COPIED,
    'create': NodeLog.FILE_ADDED,
    'update': NodeLog.FILE_UPDATED,
    'delete': NodeLog.FILE_REMOVED,
    'create_folder': NodeLog.FOLDER_CREATED,
}


@must_be_signed
@restrict_waterbutler
@must_be_valid_project
def create_waterbutler_log(payload, **kwargs):
    try:
        auth = payload['auth']
        action = LOG_ACTION_MAP[payload['action']]
    except KeyError:
        raise HTTPError(httplib.BAD_REQUEST)

    user = User.load(auth['id'])
    if user is None:
        raise HTTPError(httplib.BAD_REQUEST)

    auth = Auth(user=user)
    node = kwargs['node'] or kwargs['project']

    if action in (NodeLog.FILE_MOVED, NodeLog.FILE_COPIED):
        for bundle in ('source', 'destination'):
            for key in ('provider', 'materialized', 'name', 'nid'):
                if key not in payload[bundle]:
                    raise HTTPError(httplib.BAD_REQUEST)

        destination_node = node  # For clarity
        source_node = Node.load(payload['source']['nid'])

        source = source_node.get_addon(payload['source']['provider'])
        destination = node.get_addon(payload['destination']['provider'])

        payload['source'].update({
            'materialized': payload['source']['materialized'].lstrip('/'),
            'addon': source.config.full_name,
            'url': source_node.web_url_for(
                'addon_view_or_download_file',
                path=payload['source']['path'].lstrip('/'),
                provider=payload['source']['provider']
            ),
            'node': {
                '_id': source_node._id,
                'url': source_node.url,
                'title': source_node.title,
            }
        })

        payload['destination'].update({
            'materialized': payload['destination']['materialized'].lstrip('/'),
            'addon': destination.config.full_name,
            'url': destination_node.web_url_for(
                'addon_view_or_download_file',
                path=payload['destination']['path'].lstrip('/'),
                provider=payload['destination']['provider']
            ),
            'node': {
                '_id': destination_node._id,
                'url': destination_node.url,
                'title': destination_node.title,
            }
        })

        payload.update({
            'node': destination_node._id,
            'project': destination_node.parent_id,
        })

        if not payload.get('errors'):
            destination_node.add_log(
                action=action,
                auth=auth,
                params=payload
            )

        if payload.get('email') is True or payload.get('errors'):
            mails.send_mail(
                user.username,
                mails.FILE_OPERATION_FAILED if payload.get('errors')
                else mails.FILE_OPERATION_SUCCESS,
                action=payload['action'],
                source_node=source_node,
                destination_node=destination_node,
                source_path=payload['source']['path'],
                destination_path=payload['source']['path'],
                source_addon=payload['source']['addon'],
                destination_addon=payload['destination']['addon'],
            )
    else:
        try:
            metadata = payload['metadata']
            node_addon = node.get_addon(payload['provider'])
        except KeyError:
            raise HTTPError(httplib.BAD_REQUEST)

        if node_addon is None:
            raise HTTPError(httplib.BAD_REQUEST)

        metadata['path'] = metadata['path'].lstrip('/')

        node_addon.create_waterbutler_log(auth, action, metadata)

    return {'status': 'success'}


def get_or_start_render(file_guid, start_render=True):
    try:
        file_guid.enrich()
    except exceptions.AddonEnrichmentError as error:
        return error.as_html()

    try:
        return codecs.open(file_guid.mfr_cache_path, 'r', 'utf-8').read()
    except IOError:
        if start_render:
            # Start rendering job if requested
            build_rendered_html(
                file_guid.mfr_download_url,
                file_guid.mfr_cache_path,
                file_guid.mfr_temp_path,
                file_guid.public_download_url
            )
    return None


@must_be_valid_project
def addon_view_or_download_file_legacy(**kwargs):
    query_params = request.args.to_dict()
    node = kwargs.get('node') or kwargs['project']

    action = query_params.pop('action', 'view')
    provider = kwargs.get('provider', 'osfstorage')

    if kwargs.get('path'):
        path = kwargs['path']
    elif kwargs.get('fid'):
        path = kwargs['fid']

    if 'download' in request.path or request.path.startswith('/api/v1/'):
        action = 'download'

    if kwargs.get('vid'):
        query_params['version'] = kwargs['vid']

    # If provider is OSFstorage, check existence of requested file in the filetree
    # This prevents invalid GUIDs from being created
    if provider == 'osfstorage':
        node_settings = node.get_addon('osfstorage')

        try:
            path = node_settings.root_node.find_child_by_name(path)._id
        except NoResultsFound:
            raise HTTPError(
                404, data=dict(
                    message_short='File not found',
                    message_long='You requested a file that does not exist.'
                )
            )

    return redirect(
        node.web_url_for(
            'addon_view_or_download_file',
            path=path,
            provider=provider,
            action=action,
            **query_params
        ),
        code=httplib.MOVED_PERMANENTLY
    )


@must_be_valid_project
@must_be_contributor_or_public
def addon_view_or_download_file(auth, path, provider, **kwargs):
    extras = request.args.to_dict()
    action = extras.get('action', 'view')
    node = kwargs.get('node') or kwargs['project']

    node_addon = node.get_addon(provider)

    if not path or not node_addon:
        raise HTTPError(httplib.BAD_REQUEST)

    if not node_addon.has_auth:
        raise HTTPError(httplib.FORBIDDEN)

    if not path.startswith('/'):
        path = '/' + path

    file_guid, created = node_addon.find_or_create_file_guid(path)

    if file_guid.guid_url != request.path:
        guid_url = furl.furl(file_guid.guid_url)
        guid_url.args.update(extras)
        return redirect(guid_url)

    file_guid.maybe_set_version(**extras)

    if request.method == 'HEAD':
        download_url = furl.furl(file_guid.download_url)
        download_url.args.update(extras)
        download_url.args['accept_url'] = 'false'
        return make_response(('', 200, {'Location': download_url.url}))

    if action == 'download':
        download_url = furl.furl(file_guid.download_url)
        download_url.args.update(extras)

        return redirect(download_url.url)

    return addon_view_file(auth, node, node_addon, file_guid, extras)


def addon_view_file(auth, node, node_addon, file_guid, extras):
    render_url = node.api_url_for(
        'addon_render_file',
        path=file_guid.waterbutler_path.lstrip('/'),
        provider=file_guid.provider,
        render=True,
        **extras
    )

    ret = serialize_node(node, auth, primary=True)

    # Disable OSF Storage file deletion in DISK_SAVING_MODE
    if settings.DISK_SAVING_MODE and node_addon.config.short_name == 'osfstorage':
        ret['user']['can_edit'] = False

    ret.update({
        'provider': file_guid.provider,
        'render_url': render_url,
        'file_path': file_guid.waterbutler_path,
        'files_url': node.web_url_for('collect_file_trees'),
        'rendered': get_or_start_render(file_guid),
        # Note: must be called after get_or_start_render. This is really only for github
        'extra': json.dumps(getattr(file_guid, 'extra', {})),
        #NOTE: get_or_start_render must be called first to populate name
        'file_name': getattr(file_guid, 'name', os.path.split(file_guid.waterbutler_path)[1]),
        'materialized_path': getattr(file_guid, 'materialized', file_guid.waterbutler_path),
    })

    ret.update(rubeus.collect_addon_assets(node))
    return ret


@must_be_valid_project
@must_be_contributor_or_public
def addon_render_file(auth, path, provider, **kwargs):
    node = kwargs.get('node') or kwargs['project']

    node_addon = node.get_addon(provider)

    if not path:
        raise HTTPError(httplib.BAD_REQUEST)

    if not node_addon:
        raise HTTPError(httplib.BAD_REQUEST, {
            'message_short': 'Bad Request',
            'message_long': 'The add-on containing this file is no longer attached to the {}.'.format(node.project_or_component)
        })

    if not node_addon.has_auth:
        raise HTTPError(httplib.UNAUTHORIZED, {
            'message_short': 'Unauthorized',
            'message_long': 'The add-on containing this file is no longer authorized.'
        })

    if not node_addon.complete:
        raise HTTPError(httplib.BAD_REQUEST, {
            'message_short': 'Bad Request',
            'message_long': 'The add-on containing this file is no longer configured.'
        })

    if not path.startswith('/'):
        path = '/' + path

    file_guid, created = node_addon.find_or_create_file_guid(path)

    file_guid.maybe_set_version(**request.args.to_dict())

    return get_or_start_render(file_guid)

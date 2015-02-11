# -*- coding: utf-8 -*-
"""Utility functions for the Google Drive add-on.
"""
from website.util import web_url_for
import settings
def serialize_urls(node_settings):
    node = node_settings.owner
    urls = {
        'create' : node.api_url_for('drive_oauth_start'),
        'importAuth': node.api_url_for('gdrive_import_user_auth'),
        'deauthorize': node.api_url_for('gdrive_deauthorize'),
        'get_folders' : node.api_url_for('gdrive_folders', foldersOnly=1),
        'config': node.api_url_for('gdrive_config_put'),
        'files': node.web_url_for('collect_file_trees')
    }
    return urls


def serialize_settings(node_settings, current_user):
    """
    View helper that returns a dictionary representation of a GdriveNodeSettings record. Provides the return value for the gdrive config endpoints.
    """
    user_settings = node_settings.user_settings
    user_is_owner = user_settings is not None and (
        user_settings.owner._primary_key == current_user._primary_key
    )
    current_user_settings = current_user.get_addon('gdrive')
    rv = {
        'nodeHasAuth': node_settings.has_auth,
        'userIsOwner': user_is_owner,
        'userHasAuth': current_user_settings is not None and current_user_settings.has_auth,
        'urls': serialize_urls(node_settings)
    }
    if node_settings.has_auth:
    # Add owner's profile URL
        rv['urls']['owner'] = web_url_for('profile_view_id',
                                               uid=user_settings.owner._primary_key)
        rv['ownerName'] = user_settings.owner.fullname
        rv['access_token'] = user_settings.access_token
    return rv

def clean_path(path):
    """Ensure a path is formatted correctly for url_for."""
    if path is None:
        return ''
    return path.strip('/')

def build_gdrive_urls(item, node, path):
    newpath=clean_path(path['path'])
    return{
    'get_folders': node.api_url_for('gdrive_folders', folderId=item['id'], path=newpath, foldersOnly=1),
    'fetch': node.api_url_for('gdrive_folders', folderId=item['id'])
    }

def to_hgrid(item, node, path):
    """
    :param result: contents returned from Google Drive API
    :return: results formatted as required for Hgrid display
    """
    path = {
        'path': path + '/' + item['title'],
        'id': item['id']
    }
    serialized = {
        'addon': 'gdrive',
        'name': item['title'],
        'id': item['id'],
        'kind': 'folder',
        'urls': build_gdrive_urls(item, node, path=path),
        'path': path # as required for waterbutler path

    }
    return serialized
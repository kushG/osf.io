# encoding: utf-8

from framework.routing import Rule, json_renderer

from website.routes import OsfWebRenderer, notemplate
from website.addons.osfstorage import views


web_routes = {

    'rules': [

        Rule(
            [
                '/project/<pid>/osfstorage/files/<path:path>/',
                '/project/<pid>/node/<nid>/osfstorage/files/<path:path>/',
            ],
            'get',
            views.osf_storage_view_file,
            OsfWebRenderer('../addons/osfstorage/templates/osfstorage_view_file.mako'),
        ),

        Rule(
            [
                # Legacy routes for `view_file`
                '/project/<pid>/osffiles/<fid>/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/',
            ],
            'get',
            views.osf_storage_view_file_legacy,
            OsfWebRenderer('../addons/osfstorage/templates/osfstorage_view_file.mako'),
        ),

        Rule(
            [
                # Legacy routes for `download_file`
                '/project/<pid>/osffiles/<fid>/download/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/download/',
                # Note: Added these old URLs for backwards compatibility with
                # hard-coded links.
                '/project/<pid>/osffiles/download/<fid>/',
                '/project/<pid>/node/<nid>/osffiles/download/<fid>/',
                '/project/<pid>/files/<fid>/',
                '/project/<pid>/node/<nid>/files/<fid>/',
                '/project/<pid>/files/download/<fid>/',
                '/project/<pid>/node/<nid>/files/download/<fid>/',

                # Legacy routes for `download_file_by_version`
                '/project/<pid>/osffiles/<fid>/version/<vid>/download/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/version/<vid>/download/',
                # Note: Added these old URLs for backwards compatibility with
                # hard-coded links.
                '/project/<pid>/osffiles/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/version/<vid>/',
                '/project/<pid>/osffiles/download/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/osffiles/download/<fid>/version/<vid>/',
                '/project/<pid>/files/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/files/<fid>/version/<vid>/',
                '/project/<pid>/files/download/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/files/download/<fid>/version/<vid>/',
            ],
            'get',
            views.osf_storage_download_file_legacy,
            notemplate,
        ),

    ],
}


api_routes = {

    'prefix': '/api/v1',

    'rules': [

        Rule(
            [
                '/project/<pid>/osfstorage/files/',
                '/project/<pid>/node/<nid>/osfstorage/files/',
                '/project/<pid>/osfstorage/files/<path:path>/',
                '/project/<pid>/node/<nid>/osfstorage/files/<path:path>/',
            ],
            'get',
            views.osf_storage_get_metadata_hook,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/osfstorage/revisions/<path:path>',
                '/project/<pid>/node/<nid>/osfstorage/revisions/<path:path>',
            ],
            'get',
            views.osf_storage_get_revisions,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/osfstorage/hooks/crud/',
                '/project/<pid>/node/<nid>/osfstorage/hooks/crud/',
            ],
            'get',
            views.osf_storage_download_file_hook,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/osfstorage/hooks/crud/',
                '/project/<pid>/node/<nid>/osfstorage/hooks/crud/',
            ],
            'put',
            views.osf_storage_update_metadata_hook,
            json_renderer,
        ),
        Rule(
            [
                '/project/<pid>/osfstorage/hooks/crud/',
                '/project/<pid>/node/<nid>/osfstorage/hooks/crud/',
            ],
            'delete',
            views.osf_storage_crud_hook_delete,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/osfstorage/hooks/crud/',
                '/project/<pid>/node/<nid>/osfstorage/hooks/crud/',
            ],
            'post',
            views.osf_storage_upload_file_hook,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/osfstorage/render/<path:path>/',
                '/project/<pid>/node/<nid>/osfstorage/render/<path:path>/',
            ],
            'get',
            views.osf_storage_render_file,
            json_renderer,
        ),

        Rule(
            [
                # Legacy routes for `download_file`
                '/project/<pid>/osffiles/<fid>/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/',
                '/project/<pid>/files/download/<fid>/',
                '/project/<pid>/node/<nid>/files/download/<fid>/',

                # Legacy routes for `download_file_by_version`
                '/project/<pid>/osffiles/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/version/<vid>/',
                '/project/<pid>/files/download/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/files/download/<fid>/version/<vid>/',
            ],
            'get',
            views.osf_storage_download_file_legacy,
            json_renderer,
        ),

    ],

}

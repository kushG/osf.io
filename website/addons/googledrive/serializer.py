from website.addons.base.serializer import OAuthAddonSerializer


class GoogleDriveSerializer(OAuthAddonSerializer):

    @property
    def addon_serialized_urls(self):
        node = self.node_settings.owner
        return {
            'files': node.web_url_for('collect_file_trees'),
            'config': node.api_url_for('googledrive_config_put'),
            'deauthorize': node.api_url_for('googledrive_deauthorize'),
            'importAuth': node.api_url_for('googledrive_import_user_auth'),
            'folders': node.api_url_for('googledrive_folders'),
        }

    @property
    def serialized_node_settings(self):
        result = super(GoogleDriveSerializer, self).serialized_node_settings
        if self.node_settings.has_auth:
            path = self.node_settings.folder_path
            if path is not None:
                result['currentPath'] = '/' + path.lstrip('/')
                result['currentFolder'] = '/ (Full Google Drive)' if path == '/' else '/' + path
        return result
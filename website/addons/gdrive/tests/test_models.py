# -*- coding: utf-8 -*-
from nose.tools import *  # noqa (PEP8 asserts)

from framework.auth import Auth
from website.addons.gdrive.model import (
    AddonGdriveUserSettings, AddonGdriveNodeSettings
)
from tests.base import OsfTestCase
from tests.factories import UserFactory, ProjectFactory
from website.addons.gdrive.tests.factories import (
    GdriveNodeSettingsFactory, GdriveUserSettingsFactory
)
from website.addons.base import exceptions


class TestGdriveUserSettingsModel(OsfTestCase):

    def setUp(self):
        super(TestGdriveUserSettingsModel, self).setUp()
        self.user = UserFactory()

    def test_fields(self):
        user_settings = AddonGdriveUserSettings(
            access_token='12345',
            owner=self.user,
            username='name/email')
        user_settings.save()
        retrieved = AddonGdriveUserSettings.load(user_settings._primary_key)
        assert_true(retrieved.access_token)
        assert_true(retrieved.owner)
        assert_true(retrieved.username)

    def test_has_auth(self):
        user_settings = GdriveUserSettingsFactory(access_token=None)
        assert_false(user_settings.has_auth)
        user_settings.access_token = '12345'
        user_settings.save()
        assert_true(user_settings.has_auth)

    def test_clear_clears_associated_node_settings(self):
        node_settings = GdriveNodeSettingsFactory.build()
        user_settings = GdriveUserSettingsFactory()
        node_settings.user_settings = user_settings
        node_settings.save()
        user_settings.clear()
        user_settings.save()

        # Node settings no longer associated with user settings
        assert_is(node_settings.user_settings, None)
        assert_is(node_settings.folder, None)

    def test_clear(self):
        node_settings = GdriveNodeSettingsFactory.build()
        user_settings = GdriveUserSettingsFactory(access_token='abcde')
        node_settings.user_settings = user_settings
        node_settings.save()

        assert_true(user_settings.access_token)
        user_settings.clear()
        user_settings.save()
        assert_false(user_settings.access_token)

    def test_delete(self):
        user_settings = GdriveUserSettingsFactory()
        assert_true(user_settings.has_auth)
        user_settings.delete()
        user_settings.save()
        assert_false(user_settings.access_token)
        assert_true(user_settings.deleted)

    def test_delete_clears_associated_node_settings(self):
        node_settings = GdriveNodeSettingsFactory.build()
        user_settings = GdriveUserSettingsFactory()
        node_settings.user_settings = user_settings
        node_settings.save()

        user_settings.delete()
        user_settings.save()

        # Node settings no longer associated with user settings
        assert_is(node_settings.user_settings, None)
        assert_is(node_settings.folder, None)
        assert_false(node_settings.deleted)


class TestGdriveNodeSettingsModel(OsfTestCase):

    def setUp(self):
        super(TestGdriveNodeSettingsModel, self).setUp()
        self.user = UserFactory()
        self.user.add_addon('gdrive')
        self.user.save()
        self.user_settings = self.user.get_addon('gdrive')
        self.project = ProjectFactory()
        self.node_settings = GdriveNodeSettingsFactory(
            user_settings=self.user_settings,
            owner=self.project,
        )

    def test_fields(self):
        node_settings = AddonGdriveNodeSettings(user_settings=self.user_settings)
        node_settings.save()
        assert_true(node_settings.user_settings)
        assert_equal(node_settings.user_settings.owner, self.user)
        assert_true(hasattr(node_settings, 'folder'))

    def test_folder_defaults_to_none(self):
        node_settings = AddonGdriveNodeSettings(user_settings=self.user_settings)
        node_settings.save()
        assert_is_none(node_settings.folder)

    def test_has_auth(self):
        settings = AddonGdriveNodeSettings(user_settings=self.user_settings)
        settings.save()
        assert_false(settings.has_auth)

        settings.user_settings.access_token = '123abc'
        settings.user_settings.save()
        assert_true(settings.has_auth)

    # TODO use this test if delete function is used in gdrive/model
    # def test_delete(self):
    #     assert_true(self.node_settings.user_settings)
    #     assert_true(self.node_settings.folder)
    #     old_logs = self.project.logs
    #     self.node_settings.delete()
    #     self.node_settings.save()
    #     assert_is(self.node_settings.user_settings, None)
    #     assert_is(self.node_settings.folder, None)
    #     assert_true(self.node_settings.deleted)
    #     assert_equal(self.project.logs, old_logs)

    def test_deauthorize(self):
        assert_true(self.node_settings.user_settings)
        assert_true(self.node_settings.folder)
        self.node_settings.deauthorize(auth=Auth(self.user))
        self.node_settings.save()
        assert_is(self.node_settings.user_settings, None)
        assert_is(self.node_settings.folder, None)

        last_log = self.project.logs[-1]
        assert_equal(last_log.action, 'gdrive_node_deauthorized')
        params = last_log.params
        assert_in('node', params)
        assert_in('project', params)
        assert_in('folder', params)

    def test_set_folder(self):
        folder_name = 'queen/freddie'
        self.node_settings.set_folder(folder_name, auth=Auth(self.user))
        self.node_settings.save()
        # Folder was set
        assert_equal(self.node_settings.folder, folder_name)
        # Log was saved
        last_log = self.project.logs[-1]
        assert_equal(last_log.action, 'gdrive_folder_selected')

    def test_set_user_auth(self):
        node_settings = GdriveNodeSettingsFactory()
        user_settings = GdriveUserSettingsFactory()

        node_settings.set_user_auth(user_settings)
        node_settings.save()

        assert_true(node_settings.has_auth)
        assert_equal(node_settings.user_settings, user_settings)
        # A log was saved
        last_log = node_settings.owner.logs[-1]
        assert_equal(last_log.action, 'gdrive_node_authorized')
        log_params = last_log.params
        assert_equal(log_params['folder'], node_settings.folder)
        assert_equal(log_params['node'], node_settings.owner._primary_key)
        assert_equal(last_log.user, user_settings.owner)

    def test_serialize_credentials(self):
        self.user_settings.access_token = 'secret'
        self.user_settings.save()
        credentials = self.node_settings.serialize_waterbutler_credentials()
        expected = {'token': self.node_settings.user_settings.access_token,
                    'refresh_token': self.node_settings.user_settings.refresh_token}
        assert_equal(credentials['token'], expected['token'])
        assert_equal(credentials['refresh_token'], expected['refresh_token'])

    def test_serialize_credentials_not_authorized(self):
        self.node_settings.user_settings = None
        self.node_settings.save()
        with assert_raises(exceptions.AddonError):
            self.node_settings.serialize_waterbutler_credentials()

    def test_serialize_settings(self):
        settings = self.node_settings.serialize_waterbutler_settings()
        expected = {'folder': self.node_settings.folder}
        assert_equal(settings, expected)

    def test_serialize_settings_not_configured(self):
        self.node_settings.folder = None
        self.node_settings.save()
        with assert_raises(exceptions.AddonError):
            self.node_settings.serialize_waterbutler_settings()

    def test_create_log(self):
        action = 'file_added'
        path = '12345/camera uploads/pizza.nii'
        nlog = len(self.project.logs)
        self.node_settings.create_waterbutler_log(
            auth=Auth(user=self.user),
            action=action,
            metadata={'path': path},
        )
        self.project.reload()
        assert_equal(len(self.project.logs), nlog + 1)
        assert_equal(
            self.project.logs[-1].action,
            'gdrive_{0}'.format(action),
        )
        assert_equal(
            self.project.logs[-1].params['path'],
            path,
        )


class TestNodeSettingsCallbacks(OsfTestCase):

    def setUp(self):
        super(TestNodeSettingsCallbacks, self).setUp()
        # Create node settings with auth
        self.user_settings = GdriveUserSettingsFactory(access_token='123abc', username='name/email')
        self.node_settings = GdriveNodeSettingsFactory(
            user_settings=self.user_settings,
            folder='',
        )

        self.project = self.node_settings.owner
        self.user = self.user_settings.owner

    def test_after_fork_by_authorized_gdrive_user(self):
        fork = ProjectFactory()
        clone, message = self.node_settings.after_fork(
            node=self.project, fork=fork, user=self.user_settings.owner
        )
        assert_equal(clone.user_settings, self.user_settings)

    def test_after_fork_by_unauthorized_gdrive_user(self):
        fork = ProjectFactory()
        user = UserFactory()
        clone, message = self.node_settings.after_fork(
            node=self.project, fork=fork, user=user,
            save=True
        )
        # need request context for url_for
        assert_is(clone.user_settings, None)

    def test_before_fork(self):
        node = ProjectFactory()
        message = self.node_settings.before_fork(node, self.user)
        assert_true(message)

    def test_before_remove_contributor_message(self):
        message = self.node_settings.before_remove_contributor(
            self.project, self.user)
        assert_true(message)
        assert_in(self.user.fullname, message)
        assert_in(self.project.project_or_component, message)

    def test_after_remove_authorized_gdrive_user(self):
        message = self.node_settings.after_remove_contributor(
            self.project, self.user_settings.owner)
        self.node_settings.save()
        assert_is_none(self.node_settings.user_settings)
        assert_true(message)

    def test_after_delete(self):
        self.project.remove_node(Auth(user=self.project.creator))
        # Ensure that changes to node settings have been saved
        self.node_settings.reload()
        assert_true(self.node_settings.user_settings is None)
        assert_true(self.node_settings.folder is None)
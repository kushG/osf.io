from modularodm import fields
from website.addons.base import AddonNodeSettingsBase, AddonUserSettingsBase


class DriveUserSettings(AddonUserSettingsBase):
    """ Stores user specific information,
    including the OAuth access toke.

    """
    access_token = fields.DictionaryField(required = False)

    @property
    def has_auth(self):
        return bool(self.access_token)

class DriveNodeSettings(AddonNodeSettingsBase):
    """ Stores project specific information
    """
    user_settings = fields.ForeignField(
        'driveusersettings', backref='authorized'
    )

    @property
    def has_auth(self):
        """Whether an access token is associated with this node."""
        return bool(self.user_settings and self.user_settings.has_auth)
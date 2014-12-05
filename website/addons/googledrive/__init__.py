from . import routes, views, model


MODELS = [model.DriveNodeSettings, model.DriveUserSettings]
USER_SETTINGS_MODEL = model.DriveUserSettings
NODE_SETTINGS_MODEL = model.DriveNodeSettings
ROUTES = [routes.api_routes, routes.auth_routes, routes.web_routes]

SHORT_NAME = 'googledrive'
FULL_NAME = 'Google Drive'

OWNERS = ['user', 'node']

ADDED_DEFAULT = []
ADDED_MANDATORY = []

VIEWS = []
CONFIGS = ['user', 'node']

CATEGORIES = ['storage']

# WIDGET_HELP = 'GitHub Add-on Alpha'



# Note: Even though GitHub supports file sizes over 1 MB, uploads and
# downloads through their API are capped at 1 MB.
MAX_FILE_SIZE = 1

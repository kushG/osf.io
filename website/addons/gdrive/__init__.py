from website.addons.gdrive import routes, views, model

MODELS = [
    model.AddonGdriveUserSettings,
    model.AddonGdriveNodeSettings,
]
USER_SETTINGS_MODEL = model.AddonGdriveUserSettings
NODE_SETTINGS_MODEL = model.AddonGdriveNodeSettings

ROUTES = [routes.api_routes, routes.web_routes]

SHORT_NAME = 'gdrive'
FULL_NAME = 'Google Drive'

OWNERS = ['user', 'node']  # can include any of ['user', 'node']

VIEWS = []  # page, widget
CONFIGS = ['user','node']  # any of ['user', 'node']

CATEGORIES = ['storage']

INCLUDE_JS = {
    'page': [],
    'files': []
}

INCLUDE_CSS = {
    'page': [],
    'files': []
}

HAS_HGRID_FILES = True  # set to True for storage addons that display in HGrid
#GET_HGRID_DATA = views.hgrid.gdrive_hgrid_data
# MAX_FILE_SIZE = 10  # MB

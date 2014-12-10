import website.addons.googledrive.settings

def drive_credentials():
    return {
        'ID' : settings.CLIENT_ID,
        'SCOPE': settings.SCOPE,
        'API_KEY' : settings.API_KEY

    }
# encoding: utf-8

import hashlib

from website import settings


DOMAIN = settings.DOMAIN
UPLOAD_SERVICE_URLS = ['changeme']
PING_TIMEOUT = 5 * 60

SIGNED_REQUEST_KWARGS = {}

# HMAC options
SIGNATURE_HEADER_KEY = 'X-Signature'
URLS_HMAC_SECRET = 'changeme'
URLS_HMAC_DIGEST = hashlib.sha1
WEBHOOK_HMAC_SECRET = 'changeme'
WEBHOOK_HMAC_DIGEST = hashlib.sha1

REVISIONS_PAGE_SIZE = 10

# IDENTITY = {
#     'provider': 's3',
#     'access_key': '',
#     'secret_key': ''
# }

WATERBUTLER_CREDENTIALS = {
    'username': 'changeme',
    'token': 'changeme',
    'region': 'changeme'
}

WATERBUTLER_SETTINGS = {
    'provider': 'cloudfiles',
    'container': 'changeme',
}

WATERBUTLER_RESOURCE = 'container'

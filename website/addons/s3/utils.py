import re
from bson import ObjectId

from boto.iam import IAMConnection
from boto.s3.cors import CORSConfiguration
from boto.exception import BotoServerError

from api import get_bucket_list
import settings as s3_settings


def adjust_cors(s3wrapper, clobber=False):
    """Set CORS headers on a bucket, removing pre-existing headers set by the
    OSF. Optionally clear all pre-existing headers.

    :param S3Wrapper s3wrapper: S3 wrapper instance
    :param bool clobber: Remove all pre-existing rules. Note: if this option
        is set to True, remember to warn or prompt the user first!
    """
    rules = s3wrapper.get_cors_rules()

    # Remove some / all pre-existing rules
    if clobber:
        rules = CORSConfiguration([])
    else:
        rules = CORSConfiguration([
            rule
            for rule in rules
            if 'osf-s3' not in (rule.id or '')
        ])

    # Add new rule
    rules.add_rule(
        ['PUT', 'GET'],
        s3_settings.ALLOWED_ORIGIN,
        allowed_header=['*'],
        id='osf-s3-{0}'.format(ObjectId()),
    )

    # Save changes
    s3wrapper.set_cors_rules(rules)


def get_bucket_drop_down(user_settings):
    try:
        return [
            bucket.name
            for bucket in get_bucket_list(user_settings)
        ]
    except BotoServerError:
        return None


def create_osf_user(access_key, secret_key, name):

    connection = IAMConnection(access_key, secret_key)

    user_name = u'osf-{0}'.format(ObjectId())

    try:
        connection.get_user(user_name)
    except BotoServerError:
        connection.create_user(user_name)

    try:
        connection.get_user_policy(
            user_name,
            s3_settings.OSF_USER_POLICY
        )
    except BotoServerError:
        connection.put_user_policy(
            user_name,
            s3_settings.OSF_USER_POLICY_NAME,
            s3_settings.OSF_USER_POLICY
        )

    response = connection.create_access_key(user_name)
    access_key = response['create_access_key_response']['create_access_key_result']['access_key']
    return user_name, access_key


def remove_osf_user(user_settings):
    connection = IAMConnection(user_settings.access_key, user_settings.secret_key)
    connection.delete_access_key(
        user_settings.access_key,
        user_settings.s3_osf_user
    )
    connection.delete_user_policy(
        user_settings.s3_osf_user,
        s3_settings.OSF_USER_POLICY_NAME
    )
    return connection.delete_user(user_settings.s3_osf_user)


def validate_bucket_name(name):
    validate_name = re.compile('^(?!.*(\.\.|-\.))[^.][a-z0-9\d.-]{2,61}[^.]$')
    return bool(validate_name.match(name))

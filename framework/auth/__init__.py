# -*- coding: utf-8 -*-

from framework.sessions import session, create_session, goback
from framework import bcrypt
from framework.auth.exceptions import (
    DuplicateEmailError,
    LoginDisabledError,
    LoginNotAllowedError,
    PasswordIncorrectError,
    TwoFactorValidationError,
)
from framework.flask import redirect

from website import settings

from .core import User, Auth
from .core import get_user


__all__ = [
    'get_display_name',
    'Auth',
    'User',
    'get_user',
    'check_password',
    'authenticate',
    'login',
    'logout',
    'register_unconfirmed',
    'register',
]

def get_display_name(username):
    """Return the username to display in the navbar. Shortens long usernames."""
    if len(username) > 40:
        return '%s...%s' % (username[:20].strip(), username[-15:].strip())
    return username


# check_password(actual_pw_hash, given_password) -> Boolean
check_password = bcrypt.check_password_hash


def authenticate(user, response):
    data = session.data if session._get_current_object() else {}
    data.update({
        'auth_user_username': user.username,
        'auth_user_id': user._primary_key,
        'auth_user_fullname': user.fullname,
    })
    response = create_session(response, data=data)
    return response

def authenticate_two_factor(user):
    """Begins authentication for two factor auth users

    :param user: User to be authenticated
    :return: Response object directed to two-factor view
    """
    data = session.data if session._get_current_object() else {}
    data.update({'two_factor_auth': {
        'auth_user_username': user.username,
        'auth_user_id': user._primary_key,
        'auth_user_fullname': user.fullname,
    }})

    # Redirect to collect two factor code from user
    next_url = data.get('next_url', False)

    # NOTE: Avoid circular import /hrybacki
    from website.util import web_url_for
    if next_url:
        response = redirect(web_url_for('two_factor', next=next_url))
    else:
        response = redirect(web_url_for('two_factor'))
    response = create_session(response, data)
    return response


def user_requires_two_factor_verification(user):
    """Returns if user has two factor auth enabled

    :param user: User to be checked
    :return: True if user has two factor auth enabled
    """
    if 'twofactor' in settings.ADDONS_REQUESTED:
        two_factor_auth = user.get_addon('twofactor')
        # TODO refactor is_confirmed as is_enabled /hrybacki
        return two_factor_auth and two_factor_auth.is_confirmed
    return False


def verify_two_factor(user_id, two_factor_code):
    """Verifies user two factor authentication for specified user

    :param user_id: ID for user attempting login
    :param two_factor_code: two factor code for authentication
    :return: Response object
    """
    user = User.load(user_id)
    two_factor_auth = user.get_addon('twofactor')
    if two_factor_auth and not two_factor_auth.verify_code(two_factor_code):
        # Raise error if incorrect code is submitted
        raise TwoFactorValidationError('Two-Factor auth does not match.')

    # Update session field verifying two factor and delete key used for auth
    session.data.update(session.data['two_factor_auth'])
    del session.data['two_factor_auth']

    next_url = session.data.get('next_url', False)
    if next_url:
        response = redirect(next_url)
    else:
        # NOTE: avoid circular import /hrybacki
        from website.util import web_url_for
        response = redirect(web_url_for('dashboard'))
    return response


def login(username, password):
    """View helper function for logging in a user. Either authenticates a user
    and returns a ``Response`` or raises an ``AuthError``.

    :raises: AuthError on a bad login
    :returns: Redirect response to settings page on successful login.
    """
    username = username.strip().lower()
    password = password.strip()
    if username and password:
        user = get_user(
            username=username,
            password=password
        )
        if user:
            if not user.is_registered:
                raise LoginNotAllowedError('User is not registered.')

            if not user.is_claimed:
                raise LoginNotAllowedError('User is not claimed.')

            if user.is_disabled:
                raise LoginDisabledError('User is disabled.')

            if user_requires_two_factor_verification(user):
                return authenticate_two_factor(user)

            return authenticate(user, response=goback())
    raise PasswordIncorrectError('Incorrect password attempt.')


def logout():
    for key in ['auth_user_username', 'auth_user_id', 'auth_user_fullname']:
        try:
            del session.data[key]
        except KeyError:
            pass
    return True


def register_unconfirmed(username, password, fullname):
    user = get_user(username=username)
    if not user:
        user = User.create_unconfirmed(username=username,
            password=password,
            fullname=fullname)
        user.save()
    elif not user.is_registered:  # User is in db but not registered
        user.add_email_verification(username)
        user.set_password(password)
        user.fullname = fullname
        user.update_guessed_names()
        user.save()
    else:
        raise DuplicateEmailError('User {0!r} already exists'.format(username))
    return user


def register(username, password, fullname):
    user = get_user(username=username)
    if not user:
        user = User.create_unconfirmed(
            username=username, password=password, fullname=fullname
        )
    user.registered = True
    user.date_confirmed = user.date_registered
    user.emails.append(username)
    user.save()
    return user

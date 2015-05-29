# -*- coding: utf-8 -*-
import os
import functools
import logging
import requests

from flask import request, redirect
from werkzeug.contrib.cache import SimpleCache
from website.static_snapshot import tasks
from website.static_snapshot.utils import get_path
from website.models import Node
from website import settings


cache = SimpleCache()
logger = logging.getLogger(__name__)


# def gets_static_snapshot(page_name):
#     """
#     Performs a background celery task that calls phantom server to
#     get the static snapshot of current page.
#
#     :param page_name: Name of the page
#     :return: Decorator function
#     """
#     def wrapper(func):
#
#         @functools.wraps(func)
#         def wrapped(*args, **kwargs):
#
#             if settings.USE_CELERY:
#
#                 # Do not allow phantom or API calls to run this task
#                 if not ('Phantom' in request.user_agent.string
#                         or 'api/v1' in request.url):
#
#                     if cache.get(page_name) == 'pending':
#                         logger.warn('SEO Background task in progress')
#
#                     else:
#                         id = ''
#                         category = ''
#                         # Only public projects
#                         if kwargs.get('pid') or kwargs.get('nid'):
#                             node = Node.load(kwargs.get('pid', kwargs.get('nid')))
#                             if node.is_public:
#                                 id = kwargs.get('pid') or kwargs.get('nid')
#                                 category = 'node'
#                             else:
#                                 cache.clear()
#                                 logger.warn('Private Projects are not exposed for SEO')
#                                 return func(*args, **kwargs)
#
#                         if kwargs.get('uid'):
#                             id = kwargs.get('uid')
#                             category = 'user'
#
#                         path = get_path(page_name, id, category)
#                         if not os.path.exists(path['full_path']):
#                             task = tasks.get_static_snapshot.apply_async(args=[request.url, path['path']])
#
#                             # Retrieve these cache values in snapshot handler
#                             cache.set(page_name, 'pending')
#                             cache.set('task_id', task.id)
#                             cache.set('current_page', page_name)
#
#                         else:
#                             # Retrieving from cache, if already available
#                             with open(path['full_path'], 'r') as fp:
#                                 file_content = fp.read().decode('utf-8')
#                                 cache.set('cached_content', file_content)
#
#             return func(*args, **kwargs)
#
#         return wrapped
#
#     return wrapper


def gets_static_snapshot(pagename):
    """
    Gets Static snapshot of a page
    :param pagename: index, project, wiki, files, statistics, registrations, forks, profile
    :return: html after javascript is executed.
    """

    def wrapper(func):


        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if 'Phantom' in request.user_agent.string:
                print 'phantom'
                phantom_url = os.path.join('http://localhost:5004/', request.path)
                phantom_request = requests.get(phantom_url)
                import pdb; pdb.set_trace()
                # phantom_request = requests.get('')

            elif request.args.get('_escaped_fragment_'):

                NODE_PAGES = ['project', 'files', 'wiki', 'statistics', 'registrations', 'forks']

                if settings.USE_CELERY:

                    path = ''
                    if pagename is 'index':
                        path = os.path.join(settings.SEO_CACHE_PATH, 'index')

                    if pagename in NODE_PAGES:
                        node = Node.load(kwargs.get('pid', kwargs.get('nid')))
                        if node.is_public:
                            id = kwargs.get('pid') or kwargs.get('nid')
                            path = os.path.join(settings.SEO_CACHE_PATH, 'node', id, pagename)
                        else:
                            logger.warn('Private Projects are not exposed for SEO')
                            return {}

                    if pagename is 'profile':
                        path = os.path.join(settings.SEO_CACHE_PATH, 'user', kwargs.get('uid'), 'profile')

                    file_name = path + '.html'

                    # Check if snapshot already exists. If not, create new
                    if os.path.exists(file_name):
                        with open(file_name, 'r') as fp:
                            file_content = fp.read().decode('utf-8')
                            return file_content
                    else:
                         # Use celery task here
                        task = tasks.get_static_snapshot.apply_async(args=[request.base_url])
                        # while task.state is not 'SUCCESS':
                        #     logger.warn('still pending')
                        #     if task.state not in ['SUCCESS', 'PENDING']:
                        #         logger.warn('Invalid task')
                        #         return {}
                        # file_content = task.result['content'].encode('utf-8')
                        # with open(file_name, 'wb') as fp:
                        #     fp.write(file_content)
                        #     return file_content
                        return {'content': tasks.check_status.apply_async(args=[file_name, task.id])}
                else:
                    logger.warn('Is Celery Running?')
                    return {}
            else:
                return func(*args, **kwargs)
        return wrapped

    return wrapper



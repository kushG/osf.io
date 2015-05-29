import logging
import requests

from framework.tasks import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def get_static_snapshot(self, url):
    params = {
        'url': url,
    }
    content = {}
    response = requests.get('http://localhost:3000', params=params)
    if response.status_code == 200:
        content = response.text
        self.update_state(state='SUCCESS')
    else:
        self.update_state(state='PENDING')

    return {'content': content}


@app.task(bind=True)
def check_status(self, file_name, task_id):
    print "before error "
    task = get_static_snapshot.AsyncResult(task_id)
    while task.state is not 'SUCCESS':
        logger.warn('still pending')
        if task.state not in ['SUCCESS', 'PENDING']:
            logger.warn('Invalid task')
            return {}
    file_content = task.result['content'].encode('utf-8')
    with open(file_name, 'wb') as fp:
        fp.write(file_content)

    return file_content

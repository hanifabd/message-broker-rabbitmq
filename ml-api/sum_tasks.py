# celery -A sum_tasks worker --loglevel=INFO --pool=solo
from celery import Celery


sum_app = Celery(
    'sum_tasks', 
    broker='amqp://guest:guest@localhost:5672', 
    backend='rpc://'
)

@sum_app.task
def add(x, y):
    result = 0
    for i in range(10000000):
        result = result + 2*(x*y) / (x*y)
    return result
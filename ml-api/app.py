from flask import Flask, Response
from celery import Celery
from celery.result import AsyncResult
from sum_tasks import add, sum_app
import json


app = Flask(__name__)
celery_app = Celery(
    'sum_tasks', 
    broker='amqp://guest:guest@localhost:5672', 
    backend='rpc://'
)

@app.route('/')
def main():
    response = Response(
        json.dumps({
            "status": "ok"
        }),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/sum')
def sum():
    req_sum = add.delay(2,2)
    response = Response(
        json.dumps({
            "id": req_sum.id, 
            "status": req_sum.state,
            "result": req_sum.get()
        }),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/sum_result/<task_id>')
def task_result(task_id):
    result = AsyncResult(task_id, app=sum_app)
    if result.state != "SUCCESS":
        body = json.dumps({
            "id": result.id, 
            "status": result.state,
        })
    else:
        body = json.dumps({
            "id": result.id, 
            "status": result.state,
            "result": result.get()
        })
    
    response = Response(
        body,
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run(debug=True)
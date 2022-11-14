from flask import Flask, Response
import json
import pika
import ast


app = Flask(__name__)
connection_param = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_param)

channel = connection.channel()
channel.confirm_delivery()
channel.queue_declare('sum_events')
channel.queue_declare('sum_results_events')


@app.route('/', methods=['GET'])
def main():
    response = Response(
        json.dumps({
            "app": "green",
        }),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/sum', methods=['POST', 'GET'])
def sum():
    i = 2
    corr_id = str(i)
    body = json.dumps({
        "id": i,
        "num1": i*2,
        "num2": i+1
    })
    channel.basic_publish(
        exchange='',
        routing_key='sum_events',
        properties=pika.BasicProperties(reply_to='sum_results_events', correlation_id=corr_id),
        body=body
    )

    def on_response(ch, method, props, body):
        if corr_id == props.correlation_id:
            response = body
            print(f'Result for Id {corr_id} Operation: {response}')
            channel.stop_consuming()
    
    channel.basic_consume(
        queue='sum_results_events',
        on_message_callback=on_response,
        auto_ack=True
    )
    
    # Receive
    def on_response(ch, method, props, body):
        if corr_id == props.correlation_id:
            dict_string = body.decode('utf-8')
            data = ast.literal_eval(dict_string)
            channel.stop_consuming()

    channel.basic_consume(
        queue='sum_results_events',
        on_message_callback=on_response,
        auto_ack=True
    )
    channel.start_consuming()
    connection.close()

    response = Response(
        json.dumps({
            "result": "result.get_body()",
        }),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    app.run(debug=True)
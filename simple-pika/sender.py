import pika
import json


connection_param = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_param)

channel = connection.channel()
channel.confirm_delivery()
channel.queue_declare('sum_events')
channel.queue_declare('sum_results_events', exclusive=True)

# Send Requests to Server
try:
    
    for i in range(10):
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
        print(f'[x] Request Sent {body}')

except pika.exceptions.ConnectionClosed as exc:
    print('Error. Connection closed, and the message was never delivered.')

# Receive Response for Specific Id Request (User)
corr_id = str(5)
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
channel.start_consuming()
connection.close()
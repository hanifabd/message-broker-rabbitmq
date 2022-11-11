#!/usr/bin/env python
import pika
import ast
import json


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='sum_events')

def math_operation(num1, num2):
    result = 0
    for i in range(10000000):
        result += (num1+num2)
    return result

def callback(ch, method, props, body):
    print(f'[x] Request Received {body}')
    
    dict_string = body.decode('utf-8')
    data = ast.literal_eval(dict_string)
    id = data['id']
    num1 = data['num1']
    num2 = data['num2']
    result = math_operation(num1, num2)
    print(f'[x] Result: {result}\n')

    # Send Request Back to Client
    ch.basic_publish(
        exchange = '',
        routing_key = props.reply_to,
        properties = pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps({
            "id": id,
            "result": result
        })
    )

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='sum_events', on_message_callback=callback, auto_ack=True)

print('[*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
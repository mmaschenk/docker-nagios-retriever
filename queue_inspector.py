#!/usr/bin/env python

import os
import pika
import sys
import time

mqrabbit_user = os.getenv("MQRABBIT_USER")
mqrabbit_password = os.getenv("MQRABBIT_PASSWORD")

mqrabbit_host = os.getenv("MQRABBIT_HOST")
mqrabbit_vhost = os.getenv("MQRABBIT_VHOST")
mqrabbit_port = os.getenv("MQRABBIT_PORT")
mqrabbit_exchange = os.getenv("MQRABBIT_EXCHANGE")


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    #time.sleep(body.count(b'.'))
    time.sleep(0.1)
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)


mqrabbit_credentials = pika.PlainCredentials(mqrabbit_user, mqrabbit_password)

mqparameters = pika.ConnectionParameters(
    host=mqrabbit_host,
    virtual_host=mqrabbit_vhost,
    port=mqrabbit_port,
    credentials=mqrabbit_credentials)


mqconnection = pika.BlockingConnection(mqparameters)
channel = mqconnection.channel()

channel.exchange_declare(exchange=mqrabbit_exchange, exchange_type='fanout')

#message = ' '.join(sys.argv[1:]) or "Hello World!"
#aa = channel.basic_publish(exchange=mqrabbit_exchange, routing_key='', body=message)
#print(" [x] Sent %r" % message)
#print(aa)



result = channel.queue_declare(queue='nagios_2_receive', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=mqrabbit_exchange, queue=queue_name)

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
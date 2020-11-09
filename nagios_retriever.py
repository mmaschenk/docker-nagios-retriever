#!/usr/bin/env python3

import os
import pika
import time
import json
import requests
from requests.auth import HTTPBasicAuth

mqrabbit_user = os.getenv("MQRABBIT_USER")
mqrabbit_password = os.getenv("MQRABBIT_PASSWORD")

mqrabbit_host = os.getenv("MQRABBIT_HOST")
mqrabbit_vhost = os.getenv("MQRABBIT_VHOST", "/")
mqrabbit_port = os.getenv("MQRABBIT_PORT")
mqrabbit_exchange = os.getenv("MQRABBIT_EXCHANGE")
mqrabbit_queue = os.getenv("MQRABBIT_QUEUE")

nagiosurl = os.getenv("NAGIOS_URL")
nagiosuser = os.getenv("NAGIOS_USER")
nagiospassword = os.getenv("NAGIOS_PASSWORD")

verbose = os.getenv("VERBOSE", "False").lower() == "true"

measureinterval = int(os.getenv("MEASURE_INTERVAL", "60"))

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
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

def get_nagios_stats(url, user, password):
    response = requests.get(url, auth=(user, password))
    nagiosresult = response.json()
    servicelist = nagiosresult['data']['servicelist']
    numservices = 0
    for key, services in servicelist.items():
        for servicename, status in services.items():
            if verbose:
                print(status)
            channel.basic_publish(exchange=mqrabbit_exchange, routing_key='', body=json.dumps(status))
            numservices += 1
    print("Pushed {0} statuses to the queue".format(numservices))


if __name__ == "__main__":
    while True:
        get_nagios_stats(nagiosurl, nagiosuser, nagiospassword)
        print("\nSleeping for {} seconds\n".format(measureinterval), flush=True)
        time.sleep(measureinterval)
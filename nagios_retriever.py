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
mqrabbit_vhost = os.getenv("MQRABBIT_VHOST")
mqrabbit_port = os.getenv("MQRABBIT_PORT")
mqrabbit_exchange = os.getenv("MQRABBIT_EXCHANGE")
mqrabbit_queue = os.getenv("MQRABBIT_QUEUE")

nagiosurl = os.getenv("NAGIOS_URL")
nagiosuser = os.getenv("NAGIOS_USER")
nagiospassword = os.getenv("NAGIOS_PASSWORD")

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
    #print(nagiosresult['data']['servicelist'])
    for key, services in servicelist.items():
        #print(key)
        for servicename, status in services.items():
            #print(servicename)
            print(status)
            #print("Measured status [{0}] for [{1} @ {2}]".format(status['status'], status['description'], status['host_name']))
            channel.basic_publish(exchange=mqrabbit_exchange, routing_key='', body=json.dumps(status))


if __name__ == "__main__":
    #get_nagios_stats(
    #    'https://nagios.markschenk.nl/nagios/cgi-bin/statusjson.cgi?query=servicelist&details=true&dateformat=%25Y-%25m-%25dT%25H%3A%25M%3A%25S.%25f', 
    #    'nagiosadmin', 'gIjlBcktcEmPExDtS7bR')
    while True:
        get_nagios_stats(nagiosurl, nagiosuser, nagiospassword)
        print("\nSleeping for {} seconds\n".format(measureinterval))
        time.sleep(measureinterval)
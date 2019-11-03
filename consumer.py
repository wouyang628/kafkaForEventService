#sample sample sample

from kafka import KafkaConsumer
from json import loads
import json
from elasticsearch import Elasticsearch

consumer = KafkaConsumer(
    'eventService',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     value_deserializer=lambda x: loads(x.decode('utf-8')),
     enable_auto_commit=True,
     group_id='my-group')

es = Elasticsearch([{"host": "localhost", "port": 9200}])
for message in consumer:
    message = message.value
    print(message)
    print(message["error_message"])
    es.index(index='events', body = event1)
    

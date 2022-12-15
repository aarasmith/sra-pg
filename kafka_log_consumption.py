#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:01:20 2022

@author: andara
"""

from kafka import KafkaConsumer
import json
import db
#from dateutil import parser
#yourdate = parser.parse('2022-12-11T20:08:40.879Z')

def consume_logs(subreddit_topic, consumer_group = 'main'):
    
    consumer = KafkaConsumer(topics = subreddit_topic,
                             bootstrap_servers='44.209.117.64:9092',
                             consumer_timeout_ms=500,
                             auto_offset_reset='earliest',
                             group_id = consumer_group,
                             enable_auto_commit=False)
    consumer.poll()
    logs = [message.value for message in consumer]
    logs_decoded = [json.loads(x) for x in logs]
    log_tuple_list = [tuple(x.values()) for x in logs_decoded]
    
    with db.get_connection(search_path='conflictfootage') as con:
        cur = con.cursor()
        cur.executemany("INSERT INTO logs VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                         log_tuple_list
                         )
        con.commit()
    
    consumer.commit()
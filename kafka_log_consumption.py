#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:01:20 2022

@author: andara
"""

from kafka import KafkaConsumer
import json
import db
import configparser
#from dateutil import parser
#yourdate = parser.parse('2022-12-11T20:08:40.879Z')

def consume_logs(subreddit, consumer_group = 'main', config_file = 'connection.config'):
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    consumer = KafkaConsumer(subreddit,
                             bootstrap_servers=config['KAFKA']['BOOTSTRAP_SERVER'],
                             consumer_timeout_ms=500,
                             auto_offset_reset='earliest',
                             group_id = consumer_group,
                             enable_auto_commit=False)
    consumer.poll()
    logs = [message.value for message in consumer]
    logs_decoded = [json.loads(x) for x in logs]
    log_tuple_list = [tuple(x.values()) for x in logs_decoded]
    
    with db.get_connection(search_path=subreddit) as con:
        cur = con.cursor()
        cur.executemany("INSERT INTO logs VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                         log_tuple_list
                         )
        con.commit()
    
    consumer.commit()
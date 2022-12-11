#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 14:18:38 2022

@author: andara
"""

import logging
from kafka_logger.handlers import KafkaLoggingHandler
import configparser
import sys

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def create_kafka_logger(topic_name, logger_name = 'STDOUT', config_file = 'connection.config'):
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    config_tag = 'KAFKA'
    
    bootstrap_server = config[config_tag]['BOOTSTRAP_SERVER']
    #topic_name = config[config_tag]['TOPIC_NAME']
    
    logger = logging.getLogger(logger_name)
    
    kafka_handler_obj = KafkaLoggingHandler(
        bootstrap_server, topic_name, security_protocol="PLAINTEXT"
    )
    
    logger.setLevel(logging.DEBUG)
    
    # sl = StreamToLogger(logger, logging.INFO)
    # sys.stdout = sl
    
    return logger.addHandler(kafka_handler_obj)

def add_stdout(logger):
    sl = StreamToLogger(logger, logging.INFO)
    sys.stdout = sl

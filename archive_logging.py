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
import re
import sqs
import sns

class StreamToLogger(object): #deprecated
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


def create_kafka_logger(topic_name, logger_name, config_file = 'connection.config', exclude_progress = True):
    
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
    
    logger.addHandler(kafka_handler_obj)
    
    if exclude_progress:
        logger.addFilter(progress_filter())
    
    return(logger)

def add_stdout(logger): #deprecated
    sl = StreamToLogger(logger, logging.INFO)
    sys.stdout = sl

class progress_filter(logging.Filter):
    def filter(self, record):
        return not bool(re.search("download]\s*\d+\.*\d*%.*ETA", record.msg))

def create_sqs_logger(topic_name, logger_name, exclude_progress = True):
    logger = logging.getLogger(logger_name)
    sqs_handler_obj = sqs.SQSHandler(queue='test', aws_region='us-east-1')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(sqs_handler_obj)
    
    if exclude_progress:
        logger.addFilter(progress_filter())
    
    return(logger)

def create_sns_logger(topic_name, logger_name, exclude_progress = True):
    logger = logging.getLogger(logger_name)
    sns_handler_obj = sns.SNSHandler(topic='conflictfootage-logs', aws_region='us-east-1')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(sns_handler_obj)
    
    if exclude_progress:
        logger.addFilter(progress_filter())
    
    return(logger)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 15:57:49 2023

@author: andara
"""

import logging
import logging.handlers

import boto3
from retrying import retry
import re
import datetime
import json
import socket
import os


class SNSHandler(logging.Handler):
    """ A Python logging handler which sends messages to Amazon SNS. """

    def __init__(self,
        topic,
        aws_key_id=None,
        secret_key=None,
        aws_region=None,
        global_extra=None):
        """
        Sends log messages to SQS so downstream processors can consume
        (e.g. push the log messages to Splunk).
        :param queue: SQS queue name.
        :param aws_key_id: aws key id. Explicit credential parameters is
        not needed when running with EC2 role-based authentication.
        :param secret_key: secret key associated with the key id.
        """

        logging.Handler.__init__(self)
        if aws_key_id is None or secret_key is None:
            session = boto3.session.Session(region_name=aws_region)
        else:
            session = boto3.session.Session(aws_access_key_id=aws_key_id,
                                            aws_secret_access_key=secret_key,
                                            region_name=aws_region)

        client = session.resource('sns')
        self.topic_arn = client.create_topic(Name=topic).arn
        self.sns_client = boto3.client('sns', region_name=aws_region)
        self._global_extra = global_extra

        # When self.emit is called, the emit function will call boto3 code,
        # which in-turn will generate logs, leading to infinitely nested
        # call to the log handler (when the log handler is attached to the
        # root logger). We use this flag to guard against nested calling.
        self._entrance_flag = False

    @retry(stop_max_attempt_number=7)
    def emit(self, record):
        """
        Emit log record by sending it over to AWS SQS queue.
        """
        if self._global_extra is not None:
            record.__dict__.update(self._global_extra)

        if not self._entrance_flag:
            #msg = self.format(record)
            self.format(record)
            record.msg = re.sub('\u001B', '', record.msg, flags=re.UNICODE)
            record.message = re.sub('\u001B', '', record.message, flags=re.UNICODE)
            
            # If there's an exception, let's convert it to a string
            if record.exc_info:
                record.msg = repr(record.msg)
                record.exc_info = repr(record.exc_info)
    
            # Append additional fields
            rec = {
                    "host": socket.gethostname(),
                    "host_ip": socket.gethostbyname(socket.gethostname()),
                }
            
            for key, value in record.__dict__.items():
                if key not in ["msecs", "relativeCreated", "levelno", "created"]:
                    if key == "args":
                        # convert ALL argument to a str representation
                        # Elasticsearch supports number datatypes
                        # but it is not 1:1 - logging "inf" float
                        # causes _jsonparsefailure error in ELK
                        value = tuple(repr(arg) for arg in value)
                    if key == "msg" and not isinstance(value, str):
                        # msg contains custom class object
                        # if there is no formatting in the logging call
                        value = str(value)
                    if key == "name":
                        value = str(os.environ['CURRENT_ID'])
                    rec[key] = "" if value is None else value
                if key == "created":
                    # inspired by: cmanaha/python-elasticsearch-logger
                    created_date = datetime.datetime.utcfromtimestamp(record.created)
                    rec["timestamp"] = "{0!s}.{1:03d}Z".format(
                        created_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        int(created_date.microsecond / 1000),
                    )
            
            rec = json.dumps(rec)
            # When the handler is attached to root logger, the call on SQS
            # below could generate more logging, and trigger nested emit
            # calls. Use the flag to prevent stack overflow.
            self._entrance_flag = True
            try:
                self.sns_client.publish(TopicArn=self.topic_arn, Message=rec)
            finally:
                self._entrance_flag = False
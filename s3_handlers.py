#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 15:44:22 2022

@author: andara
"""

import boto3
import os

def move_to_s3(file_path, bucket):
    validate_bucket(bucket)
    file_name = os.path.basename(file_path)
    s3 = boto3.client('s3')
    s3.upload_file(file_path, bucket, file_name)

def list_buckets():
    return [bucket['Name'] for bucket in boto3.client('s3').list_buckets().get('Buckets')]

def validate_bucket(bucket: str, create = True):
    if set([bucket]).issubset(set(list_buckets())):
        pass
    elif create:
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucket)
        s3.put_public_access_block(
        Bucket=bucket,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
    )
    else:
        pass
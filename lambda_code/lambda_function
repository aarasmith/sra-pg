import json
import os
import sqs_log_consumption as slc

def lambda_handler(event, context):
    # TODO implement
    sr = os.environ['subreddit']
    slc.consume_logs(sr, event['Records'])
    return {
        'statusCode': 200
    }

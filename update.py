# -*- coding: utf-8 -*-

import db
import vids
import pandas as pd
import json
import boto3
import subreddit_archiver as sra
import os


def main_function(aws_region = 'us-east-1', subreddit = 'combatfootage', environment = 'dev', debug=False):
    #logger = archive_logging.create_kafka_logger(topic_name = 'archive_log')
    #archive_logging.add_stdout(logger)
    
    secret_id = f"sra/shared/{environment}"
    client = boto3.client('secretsmanager', region_name = aws_region)
    credentials = json.loads(client.get_secret_value(SecretId=secret_id)['SecretString'])
    
    sra.main.update(subreddit, batch_size=100, credentials=credentials)
    
    destinations = {
        "bucket": f"{subreddit}-{environment}",
        "log_topic": f"{subreddit}-logs-{environment}",
        "dynamo_table": f"{subreddit}-{environment}",
        "aws_region": aws_region
        }
    
    if not debug:
        try:
            s3_client = boto3.client('s3')
            s3_client.get_object(Bucket=destinations['bucket'], Key='place.txt')
        except boto3.S3.Client.exceptions.NoSuchKey:
            with open("place.txt", 'w') as f:
                f.write(str(0))
        
    proj_path = ""
    place = int(open(proj_path + 'place.txt','r').read())
    
    with db.get_connection(subreddit, credentials) as con:    
        cf_db = pd.read_sql_query(f"SELECT * FROM posts WHERE created_utc > {place}", con)
    
    cf_db = cf_db.fillna("0")
    cf_db = cf_db.loc[~cf_db.link_flair_text.str.contains("Rule 8")]
    cf_db = cf_db.loc[~cf_db.link_flair_text.str.contains("Rule 2")]
    cf_db.sort_values(by=["created_utc"], inplace=True, ascending=False)
    
    if debug:
        cf_db = cf_db.head()
    
    vids.wrapper(cf_db, destinations)
    #client = boto3.client('lambda', region_name = 'us-east-1')
    #client.invoke(FunctionName='test',InvocationType='Event',Payload=b'{"subreddit":"conflictfootage"}')
    
if __name__ == "__main__":
    main_function(aws_region=os.environ['aws_region'], subreddit=os.environ['subreddit'], environment=os.environ['environment'])

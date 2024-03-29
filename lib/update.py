# -*- coding: utf-8 -*-

import db
import vids
import pandas as pd
import json
import boto3
from subreddit_archiver import main
import os


def main_function():
    #logger = archive_logging.create_kafka_logger(topic_name = 'archive_log')
    #archive_logging.add_stdout(logger)

    aws_region=os.environ.get('AWS_REGION', 'us-east-1')
    subreddit=os.environ.get('SUBREDDIT', 'combatfootage')
    environment=os.environ.get('ENVIRONMENT', 'dev')
    if os.environ.get('DEBUG', 'false').lower() == 'true':
        debug = True
    else:
        debug = False
    if os.environ.get('UPDATE', 'true').lower() == 'true':
        update = True
    else:
        update = False
    batch_size=int(os.environ.get('BATCH_SIZE', 100))
    
    secret_id = f"sra/shared/{environment}"
    client = boto3.client('secretsmanager', region_name = aws_region)
    credentials = json.loads(client.get_secret_value(SecretId=secret_id)['SecretString'])
    
    #if archive main.archive()
    #run setup sql
    #do downloaded queue or maybe just pdf-kit everything
    #remove kafka stuff
    if update:
        main.update(subreddit, batch_size=batch_size, credentials=credentials)
    
    destinations = {
        "bucket": f"{subreddit}-{environment}",
        "log_topic": f"{subreddit}-logs-{environment}",
        "dynamo_table": f"{subreddit}-{environment}",
        "aws_region": aws_region
        }
    
    try:
        s3_client = boto3.client('s3')
        s3_client.download_file(destinations['bucket'], 'place.txt', 'place.txt')
    except s3_client.exceptions.NoSuchKey:
        with open("place.txt", 'w') as f:
            f.write(str(0))
        
    proj_path = ""
    place = int(open(proj_path + 'place.txt','r').read())
    
    with db.get_connection(subreddit, credentials) as con:    
        cf_db = pd.read_sql_query(f"SELECT * FROM posts WHERE created_utc > {place}", con)
    
    cf_db = cf_db.fillna("0")
    cf_db = cf_db.loc[~cf_db.link_flair_text.str.contains("Rule 8")]
    cf_db = cf_db.loc[~cf_db.link_flair_text.str.contains("Rule 2")]
    cf_db.sort_values(by=["created_utc"], inplace=True, ascending=True)
    
    if debug:
        cf_db = cf_db.head()
    
    vids.wrapper(cf_db, destinations)
    #client = boto3.client('lambda', region_name = 'us-east-1')
    #client.invoke(FunctionName='test',InvocationType='Event',Payload=b'{"subreddit":"conflictfootage"}')
    
if __name__ == "__main__":
    main_function()

# -*- coding: utf-8 -*-

import db
import vids
import pandas as pd
import boto3


def main_function():
    #logger = archive_logging.create_kafka_logger(topic_name = 'archive_log')
    #archive_logging.add_stdout(logger)
    
    proj_path = ""
    
    place = int(open(proj_path + 'place.txt','r').read())
    
    with db.get_connection("conflictfootage") as con:
           
        cf_db = pd.read_sql_query(f"SELECT * FROM posts WHERE created_utc > {place}", con)
        cf_db = cf_db.fillna("0")
        cf_db = cf_db.loc[~cf_db.link_flair_text.str.contains("Rule 8")]
        cf_db = cf_db.loc[~cf_db.link_flair_text.str.contains("Rule 2")]
        cf_db.sort_values(by=["created_utc"], inplace=True, ascending=False)
    
    vids.wrapper(cf_db)
    client = boto3.client('lambda', region_name = 'us-east-1')
    client.invoke(FunctionName='test',InvocationType='Event',Payload=b'{"subreddit":"conflictfootage"}')
    
if __name__ == "__main__":
    main_function()

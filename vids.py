#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 14:47:05 2022

@author: andara
"""

import db
from yt_dlp import YoutubeDL, DownloadError
import sys
import time
import os
import glob
import decimal
import json
import archive_logging
import s3_handlers

def download_videos(links_df, subreddit, save_path):
    #db connection only necessary for legacy logs
    with db.get_connection(subreddit) as con:
        cursor = con.cursor()
        #iterate over all links and log yt-dlp output with the post id as the log identifier
        #non-yt-dlp errors should be the only logs that get logged at the INFO level. yt-dlp info gets sent to debug
        for i in list(range(0, len(links_df), 1)):
            entry = links_df.iloc[i]
            url = entry.url
            file_name = save_path + "cf_vids/" + entry.id
            #logger = archive_logging.create_kafka_logger(topic_name = subreddit, logger_name = entry.id)
            logger = archive_logging.create_sqs_logger(topic_name = subreddit, logger_name = entry.id)
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": f"{file_name}.mp4",
                "cookiefile": "yt_cookies.txt",
                "noplaylist": True,
                "logger": logger,
                "writeinfojson": True
                }
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                s3_handlers.move_to_s3(file_path=f"{file_name}.mp4", bucket=subreddit, prefix=time.strftime('%Y-%m-%d'))
                os.remove(f"{file_name}.mp4")
                
                info_json = glob.glob(f"{file_name}*.json")[0]
                s3_handlers.move_to_s3(file_path=info_json, bucket=subreddit, prefix=time.strftime('%Y-%m-%d'))
                with open(info_json) as f:
                    json_metadata = json.load(f, parse_float=decimal.Decimal)
                metadata_item = {"pk":str(entry.id), "created_utc":int(entry.created_utc), "metadata":dict(json_metadata)}
                s3_handlers.insert_to_dynamodb(json_item=metadata_item, table_name=subreddit)
                os.remove(info_json)
                
                cursor.execute("INSERT INTO downloaded VALUES (%s) ON CONFLICT (id) DO NOTHING", (entry.id,))
                con.commit()
            #legacy logs - when passing a logger object to ydl_opts this stuff all gets logged and sent to kafka
            except DownloadError as ex:
                ex_type, ex_value = sys.exc_info()[0:2]
                error = (entry.id, ex_type.__name__, str(ex_value))
                cursor.execute("INSERT INTO errors VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING", error)
                con.commit()
            #non-yt-dlp errors
            except BaseException as ex:
                logger.info(f'[{type(ex)}] {ex[0]}')
                


def wrapper(links_df, subreddit = 'conflictfootage', save_path = ''):
    proj_path = ""
    #logger = archive_logging.create_kafka_logger(topic_name = subreddit, logger_name = "MAIN")
    logger = archive_logging.create_sqs_logger(topic_name = subreddit, logger_name = "MAIN")
    if len(links_df) > 0:
        
        download_videos(links_df, subreddit, save_path)
        
        old_place = str(int(open(proj_path + 'place.txt','r').read()))
        new_place = str(max(links_df.created_utc))
        
        with open(proj_path + "place.txt", 'w') as f:
            f.write(new_place)
        
        logger.info(f"Downloaded from {old_place} to {new_place} at {time.time()}")

    else:
        logger.info("Log entry: No entries to download: {time.time()}")
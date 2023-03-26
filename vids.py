#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 14:47:05 2022

@author: andara
"""

from yt_dlp import YoutubeDL, DownloadError
import time
import os
import glob
import decimal
import json
import archive_logging
import s3_handlers

def download_videos(entry, destinations, save_path):
    #iterate over all links and log yt-dlp output with the post id as the log identifier
    #non-yt-dlp errors should be the only logs that get logged at the INFO level. yt-dlp info gets sent to debug
    
    url = entry.url
    file_name = save_path + "downloads/" + entry.id
    #logger = archive_logging.create_kafka_logger(topic_name = subreddit, logger_name = entry.id)
    logger = archive_logging.create_sns_logger(topic_name = destinations['log_topic'], region=destinations['aws_region'], logger_name = entry.id)
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
        s3_handlers.move_to_s3(file_path=f"{file_name}.mp4", bucket=destinations['bucket'], prefix='videos/' + time.strftime('%Y-%m-%d'))
        os.remove(f"{file_name}.mp4")
        
        info_json = glob.glob(f"{file_name}*.json")[0]
        s3_handlers.move_to_s3(file_path=info_json, bucket=destinations['bucket'], prefix='json/' + time.strftime('%Y-%m-%d'))
        with open(info_json) as f:
            json_metadata = json.load(f, parse_float=decimal.Decimal)
        metadata_item = {"pk":str(entry.id), "created_utc":int(entry.created_utc), "metadata":dict(json_metadata)}
        s3_handlers.insert_to_dynamodb(json_item=metadata_item, table_name=destinations['dynamo_table'], region = destinations['aws_region'])
        os.remove(info_json)
        
        #processed = "Y"
        #cursor.execute("INSERT INTO downloaded VALUES (%s) ON CONFLICT (id) DO NOTHING", (entry.id,))
        #con.commit()
    #legacy logs - when passing a logger object to ydl_opts this stuff all gets logged and sent to kafka
    except DownloadError:
        pass
        #processed = "N"
    #non-yt-dlp errors
    except Exception as ex:
        logger.info(repr(ex))
    finally:
        new_place = str(entry.created_utc)          
        with open("place.txt", 'w') as f:
            f.write(new_place)
                


def wrapper(links_df, destinations, save_path = ''):
    proj_path = ""
    #logger = archive_logging.create_kafka_logger(topic_name = subreddit, logger_name = "MAIN")
    logger = archive_logging.create_sns_logger(topic_name = destinations['log_topic'], region=destinations['aws_region'], logger_name = "MAIN")
    if len(links_df) > 0:
        
        old_place = str(int(open(proj_path + 'place.txt','r').read()))
        
        for i in list(range(0, len(links_df), 1)):
            entry = links_df.iloc[i]
            try:
                download_videos(entry, destinations, save_path)
            except Exception:
                pass
            finally:
                s3_handlers.move_to_s3(file_path='place.txt', bucket=destinations['bucket'])
                new_place = str(int(open(proj_path + 'place.txt','r').read()))
                logger.info(f"Downloaded from {old_place} to {new_place} at {time.time()}")
        
    else:
        logger.info("Log entry: No entries to download: {time.time()}")
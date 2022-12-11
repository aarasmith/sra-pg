#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 14:47:05 2022

@author: andara
"""

import db
from yt_dlp import YoutubeDL
import sys
import time
import archive_logging

def download_videos(links_df):
    proj_path = ""
    with db.get_connection("conflictfootage") as con:
        cursor = con.cursor()   
        for i in list(range(0, len(links_df), 1)):
            entry = links_df.iloc[i]
            url = entry.url
            file_name = proj_path + "cf_vids/" + entry.id
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": f"{file_name}.mp4",
                "cookiefile": "yt_cookies.txt",
                "noplaylist": True,
                "logger": archive_logging.create_kafka_logger(topic_name = 'archive_logger', logger_name = entry.id)
                }
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except BaseException as ex:
                ex_type, ex_value = sys.exc_info()[0:2]
                error = (entry.id, ex_type.__name__, str(ex_value))
                cursor.execute("INSERT INTO errors VALUES (%s, %s, %s)", error)
                con.commit()
            else:
                cursor.execute("INSERT INTO downloaded VALUES (%s)", (entry.id,))
                con.commit()


def wrapper(links_df):
    proj_path = ""    
    if len(links_df) > 0:
        
        download_videos(links_df)
        
        old_place = str(int(open(proj_path + 'place.txt','r').read()))
        new_place = str(max(links_df.created_utc))
        
        with open(proj_path + "place.txt", 'w') as f:
            f.write(new_place)
        
        print(f"Log entry: Downloaded from {old_place} to {new_place} at {time.time()}")

    else:
        print("Log entry: No entries to download: {time.time()}")
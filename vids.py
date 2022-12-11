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

def download_videos(links_df):
    
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
                "noplaylist": True
                }
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except BaseException as ex:
                ex_type, ex_value = sys.exc_info()[0:2]
                error = (entry.id, ex_type.__name__, ex_value.msg)
                cursor.execute("INSERT INTO errors VALUES (%s, %s, %s)", error)
                con.commit()
            else:
                cursor.execute("INSERT INTO downloaded VALUES (%s)", entry.id)
                con.commit()


def wrapper(links_df):
        
    if len(links_df) > 0:
        
        download_videos(links_df)
        
        old_place = str(int(open(proj_path + 'place.txt','r').read()))
        new_place = str(max(links_df.created_utc))
        
        with open(proj_path + "place.txt", 'w') as f:
            f.write(new_place)
        
        print(f"Log entry: Downloaded from {old_place} to {new_place} at {time.time()}")

    else:
        print("Log entry: No entries to download: {time.time()}")
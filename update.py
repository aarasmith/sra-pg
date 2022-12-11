# -*- coding: utf-8 -*-

import db
import archive_logging
import vids
import psycopg2
import pandas as pd
import os
import yt_dlp
import sys
import time
import logging

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

if __name__ == "__main__":
    main_function()

#no_download_ids = pd.DataFrame(columns=["id_", "exception_type", "exception_message"])
#downloaded_ids = pd.DataFrame(columns=["id_"])
# if len(cf_db) > 0:
#     #no_download_ids = pd.read_parquet(proj_path + "no_download_list.parquet")
#     #downloaded_ids = pd.read_parquet(proj_path + "downloaded_list.parquet")
    
#     for i in list(range(0, len(cf_db), 1)):
#         entry = cf_db.iloc[i]
#         url = entry.url
#         file_name = proj_path + "cf_vids/" + entry.id
#         ydl_opts = {
#             "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
#             "outtmpl": f"{file_name}.mp4",
#             "cookiefile": "yt_cookies.txt",
#             "noplaylist": True
#             }
#         try:
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 ydl.download([url])
#         except BaseException as ex:
#             ex_type, ex_value = sys.exc_info()[0:2]
#             #error = pd.DataFrame({"id_": [entry.id], "exception_type": [ex_type.__name__], "exception_message": [ex_value.msg]})
#             #no_download_ids = pd.concat([no_download_ids, error])
#             error = (entry.id, ex_type.__name__, ex_value.msg)
#             cursor.execute("INSERT INTO errors VALUES (%s, %s, %s)", error)
#         else:
#             #complete = pd.DataFrame({"id_": [entry.id]})
#             cursor.execute("INSERT INTO downloaded VALUES (%s)", entry.id)
#             #downloaded_ids = pd.concat([downloaded_ids, complete])
        
    
#     #no_download_ids.to_parquet(proj_path + "no_download_list.parquet")
#     #downloaded_ids.to_parquet(proj_path + "downloaded_list.parquet")
    
#     old_place = str(place)
#     new_place = str(max(cf_db.created_utc))
    
#     with open(proj_path + "place.txt", 'w') as f:
#         f.write(new_place)
    
#     print(f"Log entry: Downloaded from {old_place} to {new_place} at {time.time()}")

# else:
#     print("Log entry: No entries to download: {time.time()}")
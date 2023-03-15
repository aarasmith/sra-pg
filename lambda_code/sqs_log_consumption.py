import json
import db

def consume_logs(subreddit, messages):
    
    logs = [json.loads(message['body']) for message in messages]
    log_tuple_list = [tuple(x.values()) for x in logs]
    
    with db.get_connection(search_path=subreddit) as con:
        cur = con.cursor()
        cur.executemany("INSERT INTO logs VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                         log_tuple_list
                         )
        con.commit()

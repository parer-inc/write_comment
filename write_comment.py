"""This service allows to write new comment to db"""
import os
import sys
import time
import MySQLdb
from rq import Worker, Queue, Connection
from methods.connection import get_redis, get_cursor

r = get_redis()


def write_comment(data):
    """Write comment into database (table comments)
       data must be a 1d array - [12]"""
    cursor, db = get_cursor()
    if not cursor or not db:
        # log that failed getting cursor
        return False
    try:
        if data is None or len(data) != 12:
            return False
        q = '''INSERT INTO  comments
                (id, video_id, channel_id, author_name,
                author_channel_id, text, parent_id,
                can_rate, likes, viewer_rating,
                published_at, updated_at, time)
                VALUES
                (%s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s, NOW() );'''
        cursor.execute(q, data)
    except Exception as error:
        print(error)
        # LOG
        return False
        # sys.exit("Error:Failed writing new comments to db")
    cursor.execute()
    db.commit()
    return True


if __name__ == '__main__':
    q = Queue('write_comment', connection=r)
    with Connection(r):
        worker = Worker([q], connection=r,  name='write_comment')
        worker.work()

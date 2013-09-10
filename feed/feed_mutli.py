#! /usr/bin/env python
# coding: utf-8

from urlparse import urlparse
from future import Future
from datetime import date, datetime, timedelta
import threading
import time

import sys
import feedparser
import mysql.connector
import socket

timeout=10
socket.setdefaulttimeout(timeout)

config = {
    'user': 'gogoreader',
    'password': 'gogoreader',
    'host': '192.168.2.108',
    'port': '5002',
    'database': 'gogoreader',
    'charset': 'utf8'
}
date_map = {
    'Feb': '02', 'Aug': '08', 'Jan': '01', 'Dec': '12',
    'Oct': '10', 'Mar': '03', 'Sep': '09', 'May': '05',
    'Jun': '06', 'Jul': '07', 'Apr': '04', 'Nov': '11'
}


class feed_parser(object):
    def __init__(self):
        self.feed_urls = None
        #self.feed_urls = None
        self.feeds = None


    def get_feed_urls(self):
        # Fix: fresh url every time is not a good choice, easy to improve
        feed_urls = []

        # Query to get all the urls and tag_id  from database
        query = ("SELECT tag_id, url FROM links_rsssource")

        # Connect to MySQL Server
        cnx = mysql.connector.connect(**config)

        # GetAbuffered cursors
        curA = cnx.cursor(buffered=True)

        # execute query in MySQL
        curA.execute(query)

        # perhaps url should be (url,)
        for (tag_id, url) in curA:
            print tag_id,url
            feed_urls.append({"url":url,"tag_id":tag_id})


        # debug:
        #print feed_urls

        curA.close()
        cnx.close()
        return feed_urls


def get_feeds(feed_urls):
    # Connect to MySQL Server
    cnx = mysql.connector.connect(**config)
    # GetAbuffered cursors
    cur = cnx.cursor(buffered=True)

    global mutex
    while True:
        url = ""
        mutex.acquire(2)
        if len(feed_urls) == 0:
            print "the feed_url length is 0,so break"
            #todo close connection
            mutex.release()
            return
        else:
            print "the feed_url length is:",len(feed_urls)
            item = feed_urls.pop()
            url = item['url']
            tag_id = item['tag_id']
        mutex.release()

        try:
            start = time.time()
            feed = feedparser.parse(url)
            consume = time.time() - start
            outputinfo = url + " " + str(tag_id) + " " + str(len(feed['items'])) + " " + str(consume)
            print outputinfo
            for item in feed['items']:
                published_time = item["updated"]
                title = item["title"]
                author = item["author"]
                link = item["link"]
                source = urlparse(link).netloc

                data = published_time.split()
                try:
                    ftime = data[3] + '-' + date_map[data[2]] + '-' + data[1] + ' ' + data[4]
                except:
                    ftime = published_time
                    pass

                line = (title, '3', ftime, '0', link, source, tag_id)
                #print line
                insert = ("INSERT IGNORE INTO links_link"
                          "(title, submitter_id, published_time, rank_score, url, source, tag_id) "
                          "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                #execute insert in MySQL
                cur.execute(insert, line)
                cnx.commit()

                #todo
                #close connections
        except Exception as e:
            print e




if __name__ == "__main__":
    thread_num = 10
    global mutex
    threads = []
    mutex = threading.Lock()

    reader = feed_parser()
    #get source url
    feed_urls = reader.get_feed_urls()

    for i in xrange(0, thread_num):
        threads.append(threading.Thread(target=get_feeds, args=(feed_urls,)))
    for t in threads:
        t.start()

    for t in threads:
        t.join()


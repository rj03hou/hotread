#! /usr/bin/env python
# coding: utf-8

from urlparse import urlparse
from future import Future
from datetime import date, datetime, timedelta

import sys
import feedparser
import mysql.connector

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

    def __init__ (self):
        self.feed_urls = None
        #self.feed_urls = None
        self.feeds = None

        self.tag_id_of_url = dict()

    def get_feed_urls(self):
        # Fix: fresh url every time is not a good choice, easy to improve
        feed_urls = list()

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
            feed_urls.append(url)
            self.tag_id_of_url[url] = tag_id

        self.feed_urls = feed_urls

        # debug: 
        print self.tag_id_of_url

        curA.close()
        cnx.close()

    def get_feeds(self):
        # pull down all feeds
        feed_tasks = [Future(feedparser.parse, feed_url) for feed_url in self.feed_urls] 
        # block until all feeds ready
        self.feeds = [feed_task() for feed_task in feed_tasks]

    def update_db(self): 
        # insert sql to update feed
        insert = ("INSERT IGNORE INTO links_link"
                "(title, submitter_id, published_time, rank_score, url, source, tag_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)")

        # Connect to MySQL Server
        cnx = mysql.connector.connect(**config)
        # GetAbuffered cursors
        cur = cnx.cursor(buffered=True)

        for feed in self.feeds:
            tag_id = self.tag_id_of_url[feed["url"]]
            for item in feed["items"]:
                published_time = item["updated"]
                title = item["title"]
                author = item["author"]
                link = item["link"]
                source = urlparse(link).netloc

                data = published_time.split()
                try:
                    time = data[3] + '-' + date_map[data[2]] + '-' + data[1] + ' ' + data[4]
                except:
                    time = published_time
                    pass

                line = (title, '3', time, '0', link, source, tag_id)
                # execute insert in MySQL
                #cur.execute(insert, line)
                #cnx.commit()
                print line

        # Make sure data is committed to the database
        cnx.commit()

        cur.close()
        cnx.close()

if __name__ == "__main__":
    reader = feed_parser()
    reader.get_feed_urls()
    reader.get_feeds()
    reader.update_db()

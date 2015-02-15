import feedparser
import re
import requests
import MySQLdb
import socket
import sys
socket.setdefaulttimeout(3)
from threading import Thread

def get_cursor():
    config = {
        'user': 'gogoreader',
        'passwd': 'gogoreader',
        'host': '127.0.0.1',
        'port': 5002,
        'db': 'gogoreader',
        'charset': 'utf8'
    }

    conn = MySQLdb.connect(**config)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('set autocommit=1')
    return cursor


def get_rss_from_url(source_url,rss):
    
    r = requests.get(source_url)
    data = r.text
    link_list =re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,data)
    count = len(link_list)

    index=0
    for url in link_list:
        print index,'/',count,url
        if url.startswith('http') and not url.startswith("http://bradsoft.co"):
            feed = feedparser.parse(url)
            if len(feed['items']) != 0:
                print "------",url
                rss.append(url)
        index = index + 1

if __name__=='__main__':
    source_urls=('http://www.zhihu.com/question/19594812','http://www.zhihu.com/question/19564031','http://www.zhihu.com/question/22608837','http://www.zhihu.com/question/26352320','http://www.zhihu.com/question/20076538','http://www.zhihu.com/question/20699036','http://www.zhihu.com/question/19870602','http://www.zhihu.com/question/20331685')
    threads = []
    rss = []
    for source_url in source_urls:
        t = Thread(target=get_rss_from_url,args=(source_url,rss))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print  "rss count",len(rss)
    cursor = get_cursor()
    for url in rss:
        cursor.execute("insert ignore into links_rsssource(url,tag_id,published_time) values('%s',1,now())"%(url))
    cursor.close()


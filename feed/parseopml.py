__author__ = 'houjunwei'
import OPML
opml = OPML.parse('/Users/houjunwei/Downloads/rss-itnews.opml')
#1:ITNEWS 2:DATABASES
tag_id = 1
import MySQLdb

CONF={
        'user':'gogoreader',
        'passwd':'gogoreader',
        'port':5002,
        'host':'192.168.2.108',
        'db':'gogoreader',
        'charset':'utf8'
}

conn = MySQLdb.connect(**CONF)
cursor = conn.cursor()
cursor.execute('set autocommit=1')

for item in opml.outlines:
    print item['title']
    for i in item.children:
        title=i['title'].replace("\\","\\\\").replace("'","''")
        xmlurl=i['xmlUrl'].replace("\\","\\\\").replace("'","''")
        insertsql="insert ignore into links_rsssource(title,published_time,description,tag_id,url) " \
                  "values('%s',now(),'%s',%d,'%s')"%(title,title,tag_id,xmlurl)
        print insertsql
        cursor.execute(insertsql)
cursor.close()
conn.close()
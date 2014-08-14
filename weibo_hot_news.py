# -*- coding: UTF-8 -*-
# rj03hou@gmail.com

import urllib
import urllib2
import httplib
import hashlib
import time
import json
import weibo
import webbrowser
import MySQLdb




ACCESS_KEY = "629c713f-b889907c-5c06dba5-6572a"
SECRET_KEY = "9f7e22be-9c5d88ba-de8d75ab-8392b"
URL = 'https://api.huobi.com/api.php'

APP_KEY = '4228096170' # app key
MY_APP_SECRET = '47b967f4877cf755f1b1fdebbddf63a7' # app secret
REDIRECT_URL = 'http://afei2.sinaapp.com/' # callback url

def get_http_response(values, url=URL):
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()



def post_weibo():
    api = weibo.APIClient(APP_KEY, MY_APP_SECRET)

    # #第一次获取的时候需要在命令行中输入浏览器后面的code，来获取access_token
    # authorize_url = api.get_authorize_url(REDIRECT_URL)
    #
    # print(authorize_url)
    #
    # webbrowser.open_new(authorize_url)
    #
    # code = raw_input()
    #
    # request = api.request_access_token(code, REDIRECT_URL)
    # access_token = request.access_token
    # expires_in = request.expires_in
    # print access_token
    # print request.expires_in
    access_token="2.00xI_xjBWxeIcE0eafacecd8qSgGQD"
    expires_in=1408561200
    api.set_access_token(access_token, expires_in)
    status = get_weibo_status()
    print api.statuses.update.post(status=status)

def get_weibo_status():

    status = u""

    config = {
        'user': 'gogoreader',
        'passwd': 'gogoreader',
        'host': '192.168.2.108',
        'port': 5002,
        'db': 'gogoreader',
        'charset': 'utf8'
    }

    conn = MySQLdb.connect(**config)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('set autocommit=1')

    cursor.execute("select * from links_link where is_post=0 order by rank_score desc limit 1")
    for row in cursor.fetchall():
        cursor.execute("update links_link set is_post=1 where id=%d"%row["id"])
        title=row["title"]
        url=row["url"]
        status+="%s %s"%(title,url)

    cursor.close()
    conn.close()
    return status

post_weibo()

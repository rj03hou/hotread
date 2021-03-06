#coding=utf8
__author__ = 'houjunwei'
import weibo
import webbrowser
import MySQLdb
import datetime
import traceback

CONF={
        'user':'gogoreader',
        'passwd':'gogoreader',
        'port':5002,
        'host':'127.0.0.1',
        'db':'gogoreader',
        'charset':'utf8'
}
#get 100 url once
STEP=100
APP_KEY = '4228096170' # app key
MY_APP_SECRET = '47b967f4877cf755f1b1fdebbddf63a7' # app secret
REDIRECT_URL = 'http://afei2.sinaapp.com/' # callback url


def get_shorturl(api,url_long):
    url_short = api.short_url.shorten.get(url_long=url_long).urls[0]["url_short"]
    #http://t.cn/z8iHJ3R,we don't need http://t.cn/
    return url_short[12:]

def get_sharecount(api,url_short):
    #{'urls': [{'share_counts': u'0', 'url_long': u'http://www.mysqlperformanceblog.com/2013/09/05/tokudb-vs-innodb-timeseries-insert-benchmark/', 'url_short': u'http://t.cn/z8iHJ3R'}]}
    return api.short_url.share.counts.get(url_short=url_short).urls[0]["share_counts"]

def get_commentcount(api,url_short):
    #{'urls': [{'share_counts': u'0', 'url_long': u'http://www.mysqlperformanceblog.com/2013/09/05/tokudb-vs-innodb-timeseries-insert-benchmark/', 'url_short': u'http://t.cn/z8iHJ3R'}]}
    return api.short_url.comment.counts.get(url_short=url_short).urls[0]["comment_counts"]

# get the score for rank, the following is the hacknews score.
# Score = (P-1) / (T+2)^G
def calc_score(weibo_sharecount,weibo_commentcount,published_time,vote_count=0,gravity=2):

    hour_age = 24
    if published_time is not None:
        time_delta = datetime.datetime.now() - published_time
        hour_age = time_delta.days*24 + time_delta.seconds / 60 / 60
    if hour_age<0:
        hour_age=999
    score = (vote_count*1 + weibo_sharecount*1.5 + weibo_commentcount*1.3 ) / pow((hour_age + 2), gravity)
    return score

def main():
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%m")
    weibo_total_request = 0
    api = weibo.APIClient(APP_KEY, MY_APP_SECRET)
    #authorize_url = api.get_authorize_url(REDIRECT_URL)
    #
    #print(authorize_url)
    #
    #webbrowser.open_new(authorize_url)
    #
    #code = raw_input()
    #
    #request = api.request_access_token(code, REDIRECT_URL)
    #access_token = request.access_token
    #expires_in = request.expires_in
    #print access_token
    #print request.expires_in

    access_token="2.002k8svBWxeIcEe9dfce56b20s5HNm"
    expires_in=1536155719
    api.set_access_token(access_token, expires_in)

    conn = MySQLdb.connect(**CONF)
    cursor = conn.cursor()
    cursor.execute('set autocommit=1')
    cursor.execute("select max(id) from links_link")
    max_id = cursor.fetchone()[0]

    strlimittime = (datetime.datetime.now() - datetime.timedelta(hours=48)).strftime('%Y-%m-%d %H:%m')
    print "strlimittime:",strlimittime

    #before 24 hours, only re calc the score, not to fetch the weibo sharecount and commentcount
    cursor.execute("select count(*) from links_link " \
                   "where published_time<='%s'"%(strlimittime))
    count = cursor.fetchone()[0]
    print "before 24'hours url count:",count
    index=0
    while(index<=max_id):
        cursor.execute("select id,published_time,url,short_url,weibo_sharecount,weibo_commentcount from links_link " \
                       "where published_time<='%s' and id>%d order by id asc limit %d"%(strlimittime,index,STEP))
        result = cursor.fetchall()
        result_len = len(result)
        if 0 == result_len:
            break
        print "index",index,result_len
        for id,published_time,url,short_url,weibo_sharecount,weibo_commentcount in result:
            try:
                #we need to calc the score, because through the time, the score is become smaller and smaller.
                score = calc_score(weibo_sharecount=weibo_sharecount,
                                   weibo_commentcount=weibo_commentcount,published_time=published_time,vote_count=0)
                #print score
                update_sql = "update links_link set short_url='%s',rank_score=%f,weibo_sharecount=%d,weibo_commentcount=%d where id=%d" \
                             %(short_url,score,weibo_sharecount,weibo_commentcount,id)
                #print update_sql
                cursor.execute( update_sql )
            except Exception as e:
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%m")
                print type(e)
                print e
                return
        index = int(result[result_len-1][0])


    #in 24 hours, should fetch the weibo sharecount and comment
    cursor.execute("select count(*) from links_link " \
                   "where published_time>'%s'"%(strlimittime))
    count = cursor.fetchone()[0]
    print "24'hours url count:",count
    index=0
    while(index<=max_id):
        cursor.execute("select id,published_time,url,short_url,weibo_sharecount,weibo_commentcount from links_link " \
                       "where published_time>'%s' and id>%d order by id asc limit %d"%(strlimittime,index,STEP))
        result = cursor.fetchall()
        result_len = len(result)
        if result_len == 0:
            break
        print "index",index,result_len
        for id,published_time,url,short_url,weibo_sharecount,weibo_commentcount in result:
            try:
                #whether the short url is initial.
                short_url_none = False
                if "" == short_url or short_url is None:
                    short_url_none = True
                    short_url = get_shorturl(api,url)
                    weibo_total_request += 1

                weibo_sharecount_new = int(get_sharecount(api,short_url))
                weibo_commentcount_new = int(get_commentcount(api,short_url))
                weibo_total_request += 2

                ##because the weibo limit the request,so now we just get the repost count,and ignore the comment count.
                ##weibo_commentcount_new = 0

                print short_url,weibo_sharecount_new,weibo_commentcount_new

                #we need to calc the score, because through the time, the score is become smaller and smaller.
                score = calc_score(weibo_sharecount=weibo_sharecount_new,
                           weibo_commentcount=weibo_commentcount_new,published_time=published_time,vote_count=0)
                update_sql = "update links_link set short_url='%s',rank_score=%f,weibo_sharecount=%d,weibo_commentcount=%d where id=%d" \
                             %(short_url,score,weibo_sharecount_new,weibo_commentcount_new,id)
                #print update_sql
                cursor.execute( update_sql )
            except weibo.APIError as e:
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%m")
                print traceback.print_exc()
                print weibo_total_request
                return
            except Exception as e:
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%m")
                print traceback.print_exc()
                return
        index = int(result[result_len-1][0])

main()

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
import sys
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')

APP_KEY = '4228096170' # app key
MY_APP_SECRET = '47b967f4877cf755f1b1fdebbddf63a7' # app secret
REDIRECT_URL = 'http://afei2.sinaapp.com/' # callback url

#http://www.btc123.com/e/interfaces/tickers.js?type=okcoinTicker
#platform:okcoin MtGox btcchina huobi fxbtc chbtc bitstamp
def get_price_from_btc123(platform):
    req = urllib2.Request('http://www.btc123.com/e/interfaces/tickers.js?type=%sTicker'%platform)
    response = urllib2.urlopen(req, timeout=3)
    result =  response.read()
    print result
    return result

def post_weibo():
    print time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time()))
    api = weibo.APIClient(APP_KEY, MY_APP_SECRET)

    ##第一次获取的时候需要在命令行中输入浏览器后面的code，来获取access_token
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

    access_token="2.00xI_xjBWxeIcE51cd36244fYG5I1B"
    expires_in=1390503601
    api.set_access_token(access_token, expires_in)
    for i in range(0,3):
        try:
            status = get_btc_weibo_status()
            print status,len(status)
            print api.statuses.update.post(status=status)
        except:
            print traceback.print_exc()
        else:
            break

def get_btc_weibo_status():

    status = u"#比特币#"

    #huobi
    result = get_price_from_btc123("huobi")
    result_json = json.loads(result)
    last = result_json["ticker"]["last"]
    high = result_json["ticker"]["high"]
    low = result_json["ticker"]["low"]
    vol = result_json["ticker"]["vol"]
    vol = int(round(float(vol)))
    status += u"【火币网】最近成交:%s,最高:%s,最低:%s,量:%s;"%(last, high, low, vol)

    #okcoin
    result = get_price_from_btc123("okcoin")
    result_json = json.loads(result)
    last = result_json["ticker"]["last"]
    high = result_json["ticker"]["high"]
    low = result_json["ticker"]["low"]
    vol = result_json["ticker"]["vol"]
    vol = int(round(float(vol)))
    status += u"【OKCoin】最近成交:%s,最高:%s,最低:%s,量:%s;"%(last, high, low, vol)

    #MtGox
    result = get_price_from_btc123("MtGox")
    result_json = json.loads(result)
    last = result_json["data"]["last"]["display_short"]
    high = result_json["data"]["high"]["display_short"]
    low = result_json["data"]["low"]["display_short"]
    vol = result_json["data"]["vol"]["value"]
    vol = int(round(float(vol)))
    status += u"【MtGox】最近成交:%s,最高:%s,最低:%s,量:%s"%(last, high, low, vol)

    return status

post_weibo()

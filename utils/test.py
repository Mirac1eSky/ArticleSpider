# -*- coding:UTF-8 -*-

import requests, time
import hmac, json
from bs4 import BeautifulSoup
from hashlib import sha1
try:
    import cookielib
except:
    import http.cookiejar as cookielib



def get_captcha(data, need_cap):
    ''' 处理验证码 '''
    if need_cap is False:
        return
    with open('captcha.gif', 'wb') as fb:
        fb.write(data)
    return input('captcha:')


def get_signature(grantType, clientId, source, timestamp):
    ''' 处理签名 '''

    hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
    hm.update(str.encode(grantType))
    hm.update(str.encode(clientId))
    hm.update(str.encode(source))
    hm.update(str.encode(timestamp))

    return str(hm.hexdigest())


def login(username, password, oncaptcha, sessiona, headers):
    ''' 处理登录 '''

    resp1 = sessiona.get('https://www.zhihu.com/signin', headers=headers)  # 拿cookie:_xsrf
    resp2 = sessiona.get('https://www.zhihu.com/api/v3/oauth/captcha?lang=cn',
                         headers=headers)  # 拿cookie:capsion_ticket
    need_cap = json.loads(resp2.text)["show_captcha"]  # {"show_captcha":false} 表示不用验证码

    grantType = 'password'
    clientId = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    source = 'com.zhihu.web'
    timestamp = str((time.time() * 1000)).split('.')[0]  # 签名只按这个时间戳变化

    captcha_content = sessiona.get('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000),
                                   headers=headers).content

    data = {
        "client_id": clientId,
        "grant_type": grantType,
        "timestamp": timestamp,
        "source": source,
        "signature": get_signature(grantType, clientId, source, timestamp),  # 获取签名
        "username": username,
        "password": password,
        "lang": "cn",
        "captcha": oncaptcha(captcha_content, need_cap),  # 获取图片验证码
        "ref_source": "other_",
        "utm_source": ""
    }


    print("**2**: " + str(data))
    print("-" * 50)
    resp = sessiona.post('https://www.zhihu.com/api/v3/oauth/sign_in', data, headers=headers).content
    print(BeautifulSoup(resp, 'html.parser'))

    print("-" * 50)
    return resp
def test():
    response = sessiona.get("https://www.zhihu.com",headers=headers)
    with open("html.html","wb") as f:
        f.write(response.text.encode("utf-8")) #转码
    print("ok")


def is_login():
    inbox_url = "https://www.zhihu.com/inbox"
    response = sessiona.get(inbox_url, headers=headers, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        print("ok")
        return True

if __name__ == "__main__":
    sessiona = requests.Session()
    sessiona.cookies = cookielib.LWPCookieJar(filename="cookies")
    try:
        sessiona.cookies.load(ignore_discard=True)
    except:
        print("未能加载cookies")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
               'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}
    #test()
    is_login()
    # login('18550821934', 'wangsw101183', get_captcha, sessiona, headers)  # 用户名密码换自己的就好了
    # resp = sessiona.get('https://www.zhihu.com/inbox', headers=headers)  # 登录进去了，可以看私信了
    # print(BeautifulSoup(resp.content, 'html.parser'))
    # sessiona.cookies.save()





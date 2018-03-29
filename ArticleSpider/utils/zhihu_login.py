#通过request登录知乎

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.3"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    "User-Agent": agent

}

def get_xsrf():
    response = requests.get("https://www.zhihu.com",headers=header)
    print(response.text)
    return ""

def zhihu_login(user,password):
    #知乎登录
    if re.match("^1\d{10}",user):
        print("phone")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf,
            "phone_num": user,
            "password": password
        }

get_xsrf()
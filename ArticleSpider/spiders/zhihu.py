# -*- coding: utf-8 -*-
import re
import hmac
import json
import scrapy
import time
import datetime
import requests
from hashlib import sha1
from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem,ZhihuQuestionItem
#兼容
try:
    import cookielib
except:
    import http.cookiejar as cookielib



class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}

    custom_settings = {
        "COOKIES_ENABLED" : True

    }

    def parse(self, response):
        #print(response.body.decode("utf-8"))
        """
        提取url 并跟踪进一步爬取
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url,url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False,all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)

                yield scrapy.Request(request_url,headers=self.headers,callback=self.parse_question,dont_filter=True)
            else:
                yield scrapy.Request(url, headers=self.headers,callback=self.parse,dont_filter=True)

    def parse_question(self,response):
        #comments_num = response.css(".QuestionHeader-Comment button::text")
        # match_obj = re.match(".*?(\d+).*",comments_num)
        # if match_obj:
        #     comments_num = int(match_obj.group(1))
        #     print(comments_num)
        # else:
        #     comments_num = 0
        # 处理question页面， 从页面中提取出具体的question item
        if "QuestionHeader-title" in response.text:
            # 处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            #item_loader.add_xpath("comments_num", "/QuestionHeader-footer//QuestionHeader-Commentbutton/button/text()")
            #item_loader.add_xpath("comments_num","")

            item_loader.add_value("watch_user_num", 0)
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

            question_item = item_loader.load_item()
        else:
            # 处理老版本页面的item提取
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                 question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title",
                                  "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#QuestionAnswers-answers > div > div > div.List-header > h4 > span::text")

            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num",
                                  "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                             callback=self.parse_answer)
        yield scrapy.Request(self.start_answer_url.format(question_id,20,0),callback=self.parse_answer)
        yield question_item

    def parse_answer(self, reponse):
        # 处理question的answer
        ans_json = json.loads(reponse.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def get_captcha(self, need_cap):
        """处理验证码 """
        if need_cap is False:
            return ""
        else:
            with open('di_captcha.gif', 'r') as fb:
                 return fb.read()
            #return input('captcha:')

    def get_signature(self, grantType, clientId, source, timestamp):
        """处理签名"""
        hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        hm.update(str.encode(grantType))
        hm.update(str.encode(clientId))
        hm.update(str.encode(source))
        hm.update(str.encode(timestamp))
        return str(hm.hexdigest())


    def start_requests(self):
        yield scrapy.Request('https://www.zhihu.com/api/v3/oauth/captcha?lang=cn',
                       headers=self.headers, callback=self.is_need_capture)

    def is_need_capture(self, response):
        yield scrapy.Request('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000),
                             headers=self.headers, callback=self.capture, meta={"resp": response})

    def capture(self, response):
        #获取图片验证码
        with open('di_captcha.gif', 'wb') as f:
            # 下载图片必须以二进制来传输
            f.write(response.body)
            f.close()

        need_cap = json.loads(response.meta.get("resp", "").text)["show_captcha"] # {"show_captcha":false}表示不用验证码
        grantType = 'password'
        clientId = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
        source = 'com.zhihu.web'
        timestamp = str(int(round(time.time() * 1000)))  # 毫秒级时间戳 签名只按这个时间戳变化

        post_data = {
            "client_id": clientId,
            "username": "18550821934",
            "password": "wangsw101183",
            "grant_type": grantType,
            "source": source,
            "timestamp": timestamp,
            "signature": self.get_signature(grantType, clientId, source, timestamp),  # 获取签名
            "lang": "cn",
            "ref_source": "homepage",
            "captcha": self.get_captcha(need_cap),  # 获取图片验证码
            "utm_source": ""
        }

        return [scrapy.FormRequest(
            url="https://www.zhihu.com/api/v3/oauth/sign_in",
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    # def check_login(self, response):
    #     # 验证是否登录成功
    #     text = json.loads(response.text)
    #     if "msg" in text and text["msg"] == "登录成功":
    #         for url in self.start_urls:
    #             yield scrapy.Request('https://www.zhihu.com/inbox', headers=self.headers,dont_filter=True)
    #
    #     print("----------------ERROR----------------------")



    def check_login(self, response):
        # 验证是否登录成功
        if 201 == response.status:
            print("----------------------ok----------------------")
            print(response)
            yield scrapy.Request('https://www.zhihu.com/inbox', headers=self.headers,dont_filter=True)


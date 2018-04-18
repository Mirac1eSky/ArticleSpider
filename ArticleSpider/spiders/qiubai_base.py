import datetime
import scrapy
import re
from scrapy.http import Request, response
from urllib import parse
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import dateconvert
from scrapy.loader import ItemLoader
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class QiubaiSpider(scrapy.Spider):
    name = 'qiubai'
    allowed_domains = ['www.qiushibaike.com']
    start_urls = ['https://www.qiushibaike.com']
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 2,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'user_trace_token=20171015132411-12af3b52-3a51-466f-bfae-a98fc96b4f90; LGUID=20171015132412-13eaf40f-b169-11e7-960b-525400f775ce; SEARCH_ID=070e82cdbbc04cc8b97710c2c0159ce1; ab_test_random_num=0; X_HTTP_TOKEN=d1cf855aacf760c3965ee017e0d3eb96; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DsXIrWUxpNGLE2g_bKzlUCXPTRJMHxfCs6L20RqgCpUq%26wd%3D%26eqid%3Dee53adaf00026e940000000559e354cc; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_hotjob; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAAFCAAEG50060B788C4EED616EB9D1BF30380575; _gat=1; _ga=GA1.2.471681568.1508045060; LGSID=20171015203008-94e1afa5-b1a4-11e7-9788-525400f775ce; LGRID=20171015204552-c792b887-b1a6-11e7-9788-525400f775ce',
            'Host': 'www.qiushibaike.com',
            'Origin': 'www.qiushibaike.com',
            'Referer': 'https://www.qiushibaike.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        }
    }

    def clear_span_br(self, txt):
        p = re.compile(r'((<span>)|(</span>)|(<br>))+')
        a = []
        for t in txt:
            a.append(p.sub(' ', t))
        return a




    def parse(self, response):
        f = open('qiushibaike.txt', 'a')
        page_url = response.selector.xpath('//ul[@class="pagination"]/li/a/@href').extract()
        author = response.selector.xpath('//div[@id="content-left"]/div/div[1]/a[2]/@title').extract()
        content = response.selector.xpath('//div[@class="content"]/span').extract()
        content = self.clear_span_br(content)
        pag_url = page_url[-1]
        while (author and content):
            a = author.pop()
            c = content.pop()
            f.write('author:' + a + '\n' + 'content:' + c + '\n')
        f.close()

        '''返回获取到的下一页的连接'''
        yield scrapy.Request("https://www.qiushibaike.com"+pag_url, callback=self.parse)





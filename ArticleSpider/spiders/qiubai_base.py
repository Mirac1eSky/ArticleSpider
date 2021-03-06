import datetime
import scrapy
import re
from ArticleSpider.items import QiushiItem,QiushiItemLoader
from urllib import parse
from scrapy.http import Request


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

    def clear_h2_br(self, txt):
        p = re.compile(r'((<h2>)|(</h2>)|(<br>))+')
        a = []
        for t in txt:
            a.append(p.sub(' ', t))
        return a

    def static_vars(**kwargs):
        def decorate(func):
            for k in kwargs:
                setattr(func, k, kwargs[k])
            return func

        return decorate
    @static_vars(page_url_exist=[])
    def parse(self, response):
        item_loader = QiushiItemLoader(item=QiushiItem(), response=response)
        user_url = response.selector.xpath('//div[@class="author clearfix"]/a/@href').extract()
        url = response.selector.xpath('//a[@class="contentHerf"]/@href').extract()
        fav_nums = response.selector.xpath('//div[@class="stats"]/span[1]/i/text()').extract()
        page_url = response.selector.xpath('//ul[@class="pagination"]/li[last()]/a/@href').extract()
        page_url = page_url.pop()
        complete_url = parse.urljoin(response.url,page_url)
        author = response.selector.xpath('//div[@id="content-left"]/div/div[1]/a[2]/h2 | //div[@id="content-left"]/div/div[1]/span[2]/h2 ').extract()
        content = response.selector.xpath('//div[@class="content"]/span[1]').extract()
        content = self.clear_span_br(content)
        author = self.clear_h2_br(author)

        #去重


        # print(author)
        # print(">>>>>>>>>>>>>>>>>>>")
        # print(content)
        if author:
            pass
        else:
            author = []
            author.append("niming")
        # with open('qiushibaike.txt', 'a') as f:
        #     while (author and content):
        #         a = author.pop()
        #         c = content.pop()
        #         print(a)
        #         print("--------------")
        #         print(c)
        #         f.write('author:' + a + '\n' + 'content:' + c + '\n')

        if complete_url not in parse.page_url_exist:
            parse.page_url_exist.append(complete_url)
            for x in parse.page_url_exist:
                print("--------------------------")
                print(len(parse.page_url_exist))
                print(complete_url)
                print("--------------------------")
            if (len(author) == len(content) and len(author) == len(url) and len(author) == len(fav_nums)):

                while (author and content and url and fav_nums):
                    item_loader = QiushiItemLoader(item=QiushiItem(), response=response)
                    item_loader.add_value("author",author.pop())
                    item_loader.add_value("content",content.pop())
                    #item_loader.add_value("url",url.pop())
                    item_loader.add_value("fav_nums",fav_nums.pop())
                    item_loader.add_value("url",parse.urljoin(response.url,url.pop()))
                    job_item = item_loader.load_item()

                    yield job_item
            else:
                print("**************************")
                print(len(author))
                print("\n")
                print(len(content))
                print("\n")
                print(len(url))
                print("\n")
                print(len(fav_nums))
                print("--------------------------")
            '''返回获取到的下一页的连接'''
            #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            #print(complete_url)
            if page_url:
                yield Request(url=complete_url, callback=self.parse,dont_filter=True)

        else:
            print("<<<<<<<<<<<<<<<<<<<")
            print("end")
            print(">>>>>>>>>>>>>>>>>>>")
            return



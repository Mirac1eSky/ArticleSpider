# -*- coding: utf-8 -*-
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


class JobbleSpider(scrapy.Spider):

    #http://blog.jobbole.com/all-posts/
    name = 'jobble'
    allowed_domains = ['blog.jobble.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="E:/SE/chromedriver.exe")
        super(JobbleSpider, self).__init__()
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def spider_closed(self,spider):
        #爬虫退出关闭browser
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        #title = response.xpath("/html/body/div[3]/div[3]/div[1]/div[1]/h1")
        #create_date = response.xpath("/html/body/div[3]/div[3]/div[1]/div[1]/h1")
        #res = response.xpath("/html/body/div[3]/div[3]/div[1]/div[1]/h1")

        """
        1.获取文章列表中的文章url并交给scrapy下载后解析
        2.获取下一页url并交给scrapy下载，完成后交给parse

        """
        posts_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for posts_node in posts_nodes:
            image_url = posts_node.css("img::attr(src)").extract_first("")
            posts_url = posts_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url,posts_url), meta={"f_image_url":image_url}, callback=self.parse_detail, dont_filter=True)
        #提取下一页并交给scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)
            print(posts_url)
            print(posts_url)

    def parse_detail(self, response):
        article_item = JobBoleArticleItem()

        # 通过css选择器提取字段
        # title = response.css(".entry-header h1::text").extract()[0]
        # front_image_url = response.meta.get("f_image_url", "")  # 文章封面图
        # create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
        # praise_nums = response.css(".vote-post-up h10::text").extract()[0]
        # fav_nums = response.css(".bookmark-btn::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        #
        # comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # content = response.css("div.entry").extract()[0]
        #
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # #article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     # print("-----------"+create_date+"------------------")
        #     # create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        #     # print("**************" +  create_date + "*********")
        #     create_date = dateconvert(create_date)
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        #
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content
        # article_item["url_obj_id"] = get_md5(response.url)

        #itemloader 加载 item
        front_image_url = response.meta.get("f_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_obj_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()



        yield article_item

        # #css选择器
        # title = response.css("head > title::text").extract()
        # f_image_url = response.meta.get("f_image_url", "") # 封面图
        # create_time =  response.css("div.entry-meta > p::text").extract()[0].strip()
        # praise_num = response.css(".vote-post-up h10::text").extract()[0]
        # collect_num = response.css(".bookmark-btn::text").extract()[0]
        # match_re = re.match(".*?(\d+).*",collect_num)
        # if match_re:
        #     collect_num = int(match_re.group(1))
        # else:
        #     collect_num = 0
        # comment_num = response.css(".hide-on-480::text").extract()[2]
        # match_re = re.match(".*?(\d+).*", comment_num)
        # if match_re:
        #     comment_num = int(match_re.group(1))
        # else:
        #     comment_num = 0
        # content = response.css("div.entry").extract()[0]
        # tags = response.css("div.entry-meta > p > a:nth-child(1)::text").extract()[0]
        # tags = [element for element in tags if not element.strip().endswith("职场")]
        # tag = ",".join(tags)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # article_item["create_date"] = create_time
        # article_item["front_image_url"] = [f_image_url]
        # article_item["comment_num"] = comment_num
        # article_item["collect_num"] = collect_num
        # article_item["praise_num"] = praise_num
        # article_item["tags"] = tag


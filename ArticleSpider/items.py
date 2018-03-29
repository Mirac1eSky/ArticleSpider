# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import dateconvert
import datetime
import re
from ArticleSpider.settings import SQL_DATETIME_FORMAT
from ArticleSpider.utils.common import extract_nums
from w3lib.html import remove_tags
from ArticleSpider.utils.common import get_salary,get_experience,handle_data
from ArticleSpider.models.es_models import Lagou

from elasticsearch_dsl.connections import connections
es = connections.create_connection(Lagou._doc_type.using)



def gen_suggests(index,info_tuple):
    #根据字符串生成搜索建议数组
    #去重
    used_words = set()
    suggests = []
    for text,weight in info_tuple:
        if text:
            #调用es接口分析字符串
            words = es.indices.analyze(index=index,analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words['tokens'] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words),"weight":weight})

    return suggests


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()



def add_jobble(value):
    return value + "-jobble"


def date_convert(vlaue):

    create_date = dateconvert(vlaue)

    return create_date


def get_nums(value):

    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment(value):
    #取出tag中的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(

    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
        output_processor=TakeFirst()
    )
    url = scrapy.Field()

    url_obj_id = scrapy.Field()

    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value),
    )
    front_image_url_path = scrapy.Field(
        output_processor=MapCompose(return_value),
    )

    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment),
        output_processor=Join(",")
    )
    content = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
          insert into article(title,create_date,url,url_obj_id,front_image_url,front_image_url_path,fav_nums,
          comment_nums,praise_nums,content,tags) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
        params = (self["title"], self["create_date"],
                                    self["url"],  self["url_obj_id"],
                                    self["front_image_url"],self["front_image_url_path"],
                                    self["fav_nums"],self["comment_nums"],
                                    self["praise_nums"],self["content"],self["tags"])

        return insert_sql,params


class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_nums("".join(self["answer_num"]))
        comments_num = extract_nums("".join(self["comments_num"]))


        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    #知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, parise_num, comments_num,
              create_time, update_time, crawl_time
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), parise_num=VALUES(parise_num),
              update_time=VALUES(update_time)
        """

        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["parise_num"],
            self["comments_num"], create_time, update_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params


def replace_splash(value):
    return value.replace("/", "")

def handle_strip(value):
    return value.strip()

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #拉勾网职位
    title = scrapy.Field()
    url = scrapy.Field()
    url_obj_id = scrapy.Field()
    tags = scrapy.Field(
        input_processor = Join(",")
    )
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(handle_strip),
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field(
        input_processor=MapCompose(handle_strip),
    )
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """
            insert into lagou(title, url,url_obj_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_url, company_name, job_id,tags,minsalary,maxsalary
            
            ,crawl_time,min_work_year,max_work_year)
            VALUES (%s, %s,%s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE 
            job_desc=VALUES(job_desc),url_obj_id=VALUES(url_obj_id),publish_time=VALUES(publish_time)
        """

        minsalary,maxsalary = get_salary(self["salary"])
        min_work_year,max_work_year = get_experience(self["work_years"])
        publish_time = handle_data(self["publish_time"])
        job_id = extract_nums(self["url"])
        print("job_id")
        params = (self["title"], self["url"], self["url_obj_id"], self["salary"], self["job_city"], self["work_years"], self["degree_need"],
                  self["job_type"], publish_time, self["job_advantage"], self["job_desc"], self["job_addr"], self["company_url"],
                  self["company_name"], job_id,self["tags"],minsalary,maxsalary, self["crawl_time"].strftime(SQL_DATETIME_FORMAT),min_work_year
                  ,max_work_year)

        return insert_sql, params


    def save_to_es(self):
        minsalary, maxsalary = get_salary(self["salary"])
        min_work_year, max_work_year = get_experience(self["work_years"])
        publish_time = handle_data(self["publish_time"])
        lagou = Lagou()
        lagou.title = self['title']
        lagou.url = self['url']
        lagou.min_work_year = min_work_year
        lagou.max_work_year = max_work_year
        lagou.min_salary = minsalary
        lagou.max_salary = maxsalary
        lagou.publish_time = publish_time
        if self['tags'] == None:
            lagou.tags = None
        else:
            lagou.tags = self['tags']
        lagou.company_name = self['company_name']
        lagou.job_addr = self['job_addr']
        lagou.job_advantage = self['job_advantage']
        lagou.job_city = self['job_city']
        lagou.job_desc = remove_tags(self['job_desc'])
        lagou.degree_need = self['degree_need']
        lagou.meta.id = self['url_obj_id']
        lagou.suggest = gen_suggests(Lagou._doc_type.index,((lagou.title,10),(lagou.tags,7)))

        #lagou.suggest = [{"input":[],"weight":2}]
        lagou.save()

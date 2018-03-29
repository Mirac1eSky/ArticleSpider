# -*- coding: utf-8 -*-

import codecs
import json
import MySQLdb
import MySQLdb.cursors
from datetime import date,datetime
from ArticleSpider.models.es_models import Lagou
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
from w3lib.html import remove_tags
from ArticleSpider.utils.common import get_experience,get_salary,handle_data

class DataJson(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj,date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self,obj)


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonwithEncodingPipeline(object):
    #自定义导入json
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding="utf-8")

    def process_item(self, item, spider):
        #lines = jsonT.MyEncoder(dict(item))
        lines = json.dumps(dict(item), ensure_ascii=False,cls=DataJson) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

class JsonExporterPipleline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


#下载图片
class ArticlesImagepiderPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        #print("gggggggggggggggggggggg")
        #if "front_image_url_path" in item:
        for ok, value in results:
            print("*****************************************")
            image_file_path = value["path"]
            print("image_file_path===="+image_file_path)
            print("+++++++++++++++++++++++++++++++++++++++++")
        item["front_image_url_path"] = image_file_path
        return item


#同步保存到DB
class MysqlPipeline(object):
    def __init__(self):
        # self.conn = MySQLdb.connect('host','user','pwd','db name',charset="utf8")
        self.conn = MySQLdb.connect('localhost', 'root', 'root', 'article_spider', charset="utf8", use_unicode = True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # insert_sql = """
        #   insert into article(title,create_date,url,url_obj_id,front_image_url,front_image_url_path,fav_nums,
        #   comment_nums,praise_nums，content) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,)
        #
        # """
        insert_sql = """
                    insert into article(title, url,  create_date, fav_nums)
                    VALUES (%s, %s, %s, %s)
                """
        self.cursor.execute(insert_sql, (item["title"],item["url"], item["create_date"], item["fav_nums"]))
        self.conn.commit()

#异步保存到DB
class MysqlTwistedPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
        host = settings["MYSQL_HOST"],
        db = settings["MYSQL_DBNAME"],
        user = settings["MYSQL_USER"],
        password = settings["MYSQL_PASSWORD"],
        charset = 'utf8',
        cursorclass = MySQLdb.cursors.DictCursor,
        use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)

        return cls(dbpool)


    def process_item(self, item, spider):

        #使用twisted 异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self, failure, item, spider):
        print(failure)


    def do_insert(self, cursor, item):
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class ElasticSearchPipeline(object):
    def process_item(self,item,spider):
        item.save_to_es()
        return item
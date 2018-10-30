# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
import pymongo
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class JobbolePipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']
            item["front_image_path"] = image_file_path

            return item


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()


class JsonWithEncodingPipeline(object):
    # 自定义json导出文件
    def __init__(self):
        self.file = codecs.open('jobbole.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
       lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
       self.file.write(lines)
       return item

    def close_spider(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('jobboleexporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
       self.exporter.export_item(item)
       return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('10.112.214.168', 'root', '123456', 'ArticleSpider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
       insert_sql = """
            insert into jobbole_article(title,create_time,url,url_object_id,front_image_url,front_image_path,
            comment_nums,vote_nums,mark_nums,tags,content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
       """
       self.cursor.execute(insert_sql, (item['title'], item['create_time'], item['url'], item['url_object_id'],
                                        item['front_image_url'], item['front_image_path'], item['comment_nums'],
                                        item['vote_nums'], item['mark_nums'], item['tags'], item['content'],))
       self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWD"],
            db=settings["MYSQL_DBNAME"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item)   # 处理异常

    def handle_error(self, failure, item):
        # 处理异步异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item构建不同的SQL语句并插入到不同的mysql中
        insert_sql, params = item.get_insetsql()
        cursor.execute(insert_sql, params)

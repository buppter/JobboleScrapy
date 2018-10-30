# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re

from scrapy import Field
from scrapy import Item
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import datetime
from scrapy.loader import ItemLoader
from jobbole.utils.common import extract_num
from jobbole.settings import SQL_DATE_FORMAT, SQL_DATETIME_FORMAT


def date_convert(value):
    try:
        create_time = datetime.datetime.strptime(value, '%Y/%m/%s').date()
    except Exception as e:
        create_time = datetime.datetime.now().date()
    return create_time


def get_nums(value):
    match_re = re.match('.*?(\d+).*?', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_form_tags(value):
    # 去掉tags中的提取的评论
    if '评论' in value:
        return ""
    else:
        return value


def return_valur(value):
    return value


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class JobboleItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # title = Field()
    # create_time = Field()
    # vote_nums = Field()
    # url = Field()
    # url_object_id = Field()
    # mark_nums = Field()
    # comment_nums = Field()
    # tags = Field()
    # content = Field()
    # front_image_url = Field()
    # front_image_path = Field()
    title = Field(
        input_processor=MapCompose(lambda x: x + '-jobbole'),
    )
    create_time = Field(
        input_processor=MapCompose(date_convert),
    )
    vote_nums = Field(
        input_processor=MapCompose(get_nums)
    )
    url = Field()
    url_object_id = Field()
    mark_nums = Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = Field(
        input_processor=MapCompose(get_nums)
    )
    tags = Field(
        input_processor=MapCompose(remove_comment_form_tags),
        output_processor=Join(",")
    )
    content = Field()
    front_image_url = Field(
        output_processor=MapCompose(return_valur)
    )
    front_image_path = Field()

    def get_insetsql(self):
        insert_sql = """
                    insert into jobbole_article(title,create_time,url,url_object_id,front_image_url,front_image_path,
                    comment_nums,vote_nums,mark_nums,tags,content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               """
        parms = (self['title'], self['create_time'], self['url'], self['url_object_id'],
                 self['front_image_url'], self['front_image_path'], self['comment_nums'],
                 self['vote_nums'], self['mark_nums'], self['tags'], self['content'])
        return insert_sql, parms

class ZhihuQuestionItem(Item):
    # 知乎问题item
    zhihu_id = Field()
    topic = Field()
    url = Field()
    title = Field()
    content = Field()
    answer_num = Field()
    comments_num = Field()
    click_num = Field()
    watch_user_num = Field()
    crawl_time = Field()

    def get_insetsql(self):
        # 插入知乎question的SQL语句
        insert_sql = """
                    insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,
                    watch_user_num,click_num,crawl_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), 
                    comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num), 
                    click_num=VALUES(click_num)
               """
        zhihu_id = self["zhihu_id"][0]
        topic = ",".join(self["topic"])
        url = "".join(self["url"])
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = int(self["watch_user_num"][1].replace(',', ''))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id, topic, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(Item):
    # 知乎回答item
    zhihu_id = Field()
    url = Field()
    question_id = Field()
    author_id = Field()
    content = Field()
    praise_num = Field()
    comments_num = Field()
    create_time = Field()
    update_time = Field()
    crawl_time = Field()

    def get_insetsql(self):
        # 插入知乎question的SQL语句
        insert_sql = """
                           insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_num,comments_num,
                           create_time,update_time,crawl_time)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           ON DUPLICATE KEY UPDATE content = VALUES(content),comments_num=VALUES(comments_num),
                           update_time=VALUES(update_time)
                      """
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        if self['update_time']:
            update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        else:
            update_time = None
        print(self['create_time'], self['update_time'])
        print(create_time, update_time)
        params = (self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'],
                 self['praise_num'], self['comments_num'], create_time, update_time,
                 self['crawl_time'].strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params


class ZakerItem(Item):
    # ZAKER的item
    url_id = Field()
    article_url = Field()
    title = Field()
    media = Field()
    comments_num = Field()
    img_url = Field()
    article_content = Field()
    original_url = Field()
    tags = Field()
    parse_time = Field()

    def get_insetsql(self):
        # 插入zaker的SQL语句
        insert_sql = """
                           insert into zaker(url_id,article_url,title,media,comments_num,img_url,article_content,
                           original_url,tags,parse_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                      """
        url_id = "".join(self['url_id'])
        article_url = "".join(self['article_url'])
        title = "".join(self['title'])
        media = "".join(self['media'])
        comments_num = extract_num("".join(self['comments_num']))
        if comments_num:
            comments_num = comments_num
        else:
            comments_num = 0

        img_url = "".join(self['img_url'])
        article_content = ",".join(self['article_content'])
        original_url = "".join(self['original_url'])
        if self['tags'] == '无':
            tags = '无'
        else:
            tags = ",".join(self['tags'])
        parse_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (url_id, article_url, title, media, comments_num, img_url, article_content, original_url, tags,
                  parse_time)
        return insert_sql, params

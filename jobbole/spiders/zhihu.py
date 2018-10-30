# -*- coding: utf-8 -*-
import datetime

import scrapy
import json
import re
from urllib import parse
from scrapy.loader import ItemLoader
from jobbole.items import ZhihuAnswerItem, ZhihuQuestionItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = [
        'file:///C:/Users/SXT/Desktop/%E7%9F%A5%E4%B9%8E%20-%20%E5%8F%91%E7%8E%B0%E6%9B%B4%E5%A4%A7%E7%9A%84%E4%B8%96%E7%95%8C.html']
    # question的第一页answer的请求URL
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D." \
                       "is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2" \
                       "Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2" \
                       "Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2" \
                       "Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2" \
                       "Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2" \
                       "Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D." \
                       "url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D." \
                       "topics&limit={1}&offset={2}&sort_by=default"

    def parse(self, response):
        """
        提取HTML页面中的所有URL，并跟踪这些URL进一步爬取
        如果提取的URL中格式为/question/XXX 就下载之后直接进入解析函数
        """
        all_urls = response.css('h2 a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith(
            "https") else False, all_urls)
        # = if url.startswith("https"):
        for url in all_urls:
            match_obj = re.match('(.*?zhihu.com/question/(\d+))(/|$).*?', url)
            if match_obj:
                # 如果提取到question相关页面则下载后交由提取函数进行解析
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, callback=self.parse_question, dont_filter=True)
                break
            else:
                pass
                # 如果不是question页面，则直接进一步跟踪
                # yield scrapy.Request(url, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面， 从question页面提取question item
        match_obj = re.match(
            '(.*?zhihu.com/question/(\d+))(/|$).*?',
            response.url)
        if match_obj:
            question_id = int(match_obj.group(2))
            item_loader = ItemLoader(
                item=ZhihuQuestionItem(),
                response=response,
                dont_filter=True)
            item_loader.add_css(
                "title", ".QuestionHeader .QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionRichText")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css(
                "comments_num",
                ".QuestionHeader-Comment button::text")
            item_loader.add_css(
                "watch_user_num",
                ".NumberBoard-itemValue::text")
            item_loader.add_css(
                "topic", ".QuestionHeader-topics .Tag-content .Popover div::text")
            question_item = item_loader.load_item()
            yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), callback=self.parse_answer, dont_filter=True)
            # yield question_item

    def parse_answer(self, response):
        # 处理answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['praise_num'] = answer['voteup_count'] if 'voteup_count' in answer else None
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time'] if 'updated_time' in answer else None
            answer_item['comments_num'] = answer['comment_count'] if 'comment_count' in answer else None
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, callback=self.parse_answer, dont_filter=True)

        '''
        def start_requests(self):
            return [scrapy.Request('https://www.zhihu.com/api/v3/oauth/sign_in', callback=self.login)]

        def login(self, response):
            response_text = response.text
            match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
            xsrf = ''
            if match_obj:
                xsrf = (match_obj.group(1))

            if xsrf:
                post_url = "https://www.zhihu.com/login/phone_num"
                post_data = {
                    "_xsrf": xsrf,
                    "phone_num": "18782902568",
                    "password": "admin123"
                }

                return [scrapy.FormRequest(
                    url=post_url,
                    formdata=post_data,
                    headers=self.headers,
                    callback=self.check_login
                )]

        def check_login(self, response):
            # 验证服务器的返回数据判断是否成功
            text_json = json.loads(response.text)
            if "msg" in text_json and text_json["msg"] == "登录成功":
                for url in self.start_urls:
                    yield scrapy.Request(url, dont_filter=True, headers=self.headers)
        '''

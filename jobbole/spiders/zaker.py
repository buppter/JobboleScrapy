# -*- coding: utf-8 -*-
import datetime
import json
from scrapy.http import Request
import scrapy
from urllib import parse
from scrapy.loader import ItemLoader
from jobbole.items import ZakerItem
from jobbole.utils.common import get_md5


class ZakerSpider(scrapy.Spider):
    name = 'zaker'
    allowed_domains = ['www.zaker.com']
    start_urls = ['http://www.myzaker.com/news/next_new.php?f=myzaker_com&url=http%3A%2F%2Fiphone.myzaker.com%2Fzaker%2Fblog2news.php%3Fapp_id%3D660%26since_date%3D1529667611%26nt%3D2%26next_aticle_id%3D5b2d0c069490cb8b3d000052%26_appid%3Diphone%26opage%3D3%26otimestamp%3D153%26top_tab_id%3D12183%26_version%3D6.5&_version=6.5']

    def parse(self, response):
        res = json.loads(response.text)
        article = res['data']['article']
        print(len(article))
        for i in range(len(article)):
            article_url = article[i]['href']
            title = article[i]['title']
            media = article[i]['marks'][0]
            marks = article[i]['marks']
            comments_num = [element for element in marks if element.strip().endswith("评论")]
            img_url = article[0]['img']
            yield Request(url=(parse.urljoin(response.url, article_url)), callback=self.parse_detail, dont_filter=True,
                          meta={
                              "article_url": article_url,
                              "title": title,
                              "media": media,
                              "comments_num": comments_num,
                              "img_url": img_url
                          })
        next_url = res['data']['next_url']
        yield Request(parse.urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        # article_content = response.css('.article_content #content').extract()
        # article_content = response.xpath('//div[@class="article_content"]/div[@id="content"]').extract()
        # original_url = response.css('.article_detail a::attr(href)').extract_first()
        # # original_url = response.xpath('//div[@class="article_detail"]/a/@href').extract_first()
        tags = response.css('.article_more a::text').extract()
        if tags:
            tags = tags
        else:
            tags = '无'
        # # tags = response.xpath('//*[@class="article_more"]/a/text()').extract()

        item_loader = ItemLoader(
            item=ZakerItem(),
            response=response,
            dont_filter=True
        )

        item_loader.add_value('url_id', get_md5(response.url))
        item_loader.add_value('article_url', response.url)
        item_loader.add_value('title', response.meta.get('title'))
        item_loader.add_value('media', response.meta.get('media'))
        item_loader.add_value('comments_num', response.meta.get('comments_num'))
        item_loader.add_value('img_url', response.meta.get('img_url'))
        item_loader.add_css('article_content', '.article_content #content')
        item_loader.add_css('original_url', '.article_detail a::attr(href)')
        item_loader.add_value('tags', tags)
        # item_loader.add_value('parse_time', datetime.datetime.now())
        article_item = item_loader.load_item()
        yield article_item


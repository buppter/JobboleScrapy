# -*- coding: utf-8 -*-
import scrapy


class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    allowed_domains = ['https://tieba.baidu.com/f?kw=%E6%9D%8E%E6%AF%85']
    start_urls = ['https://tieba.baidu.com/']

    def parse(self, response):
        pass

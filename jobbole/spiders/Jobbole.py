# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from jobbole.items import JobboleItem, ArticleItemLoader
from jobbole.utils.common import get_md5
import datetime
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'Jobbole'
    allowed_domains = ['www.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的URL并交给scrapy下载后进行解析
        2.获取下一页的URL英并交给scrapy进行下载，下载完成后交给parse
        """
        # 解析列表页中的所有URL并交给scrapy进行下载后解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first("")
            post_url = post_node.css('::attr(href)').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url},
                          callback=self.parse_detail, dont_filter=True)

        # 提取下一页并进行下载
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        '''
        article_item = JobboleItem()
        # 提取文章的具体字段

        # 文章图片
        front_image_url = response.meta.get("front_image_url", "")

        #文章标题
        title = response.css('.entry-header h1::text').extract_first()
        # title = response.xpath("//div[@class='entry-header']/h1/text()").extract_first()

        # 创建时间
        create_time = response.css('.entry-meta-hide-on-mobile::text').extract_first().strip().replace(' ·', '')
        # create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(' ·', '')

        # 点赞数量
        vote_nums = response.css('.vote-post-up h10::text').extract_first()
        # vote_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first()
        if vote_nums:
            vote_nums = int(vote_nums)
        else:
            vote_nums = 0

        # 收藏数量
        mark_nums = response.css('.bookmark-btn::text').extract_first()
        # mark_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract_first()
        match_re = re.match('.*?(\d+).*?', mark_nums)
        if match_re:
            mark_nums = int(match_re.group(1))
        else:
            mark_nums = 0

        # 评论数量
        comment_nums = response.css('.btn-bluet-bigger.href-style.hide-on-480::text').extract_first()
        # comment_nums = response.xpath('//span[@class="btn-bluet-bigger href-style hide-on-480"]/text()').extract_first()
        match_re = re.match('.*?(\d+).*?', comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        # 文章内容，这里只提取HTML
        connent = response.css('.entry').extract_first()
        # content = response.xpath('//div[@class="entry"]').extract_first()

        # 标签
        tags_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        # tags = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tags_list = [element for element in tags_list if not element.strip().endswith("评论")]
        tags = ','.join(tags_list)

        article_item["title"] = title
        article_item["url"] = response.url
        try:
            create_time = datetime.datetime.strptime(create_time, '%Y/%m/%s').date()
        except Exception as e:
            create_time = datetime.datetime.now().date()
        article_item["create_time"] = create_time
        article_item["vote_nums"] = vote_nums
        article_item["mark_nums"] = mark_nums
        article_item["comment_nums"] = comment_nums
        article_item["content"] = connent
        article_item["tags"] = tags
        article_item["front_image_url"] = [front_image_url]
        article_item["url_object_id"] = get_md5(response.url)
        '''
        # 通过itemloader加载item
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = ArticleItemLoader(item=JobboleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        # item_loader.add_xpath()
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('create_time', '.entry-meta-hide-on-mobile::text')
        item_loader.add_css('vote_nums', '.vote-post-up h10::text')
        item_loader.add_css('mark_nums', '.bookmark-btn::text')
        item_loader.add_css('comment_nums', '.btn-bluet-bigger.href-style.hide-on-480::text')
        item_loader.add_css('tags', '.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('content', '.entry')
        article_item = item_loader.load_item()
        yield article_item



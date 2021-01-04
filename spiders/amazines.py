# -*- coding: utf-8 -*-
import scrapy


class AmazinesSpider(scrapy.Spider):
    name = 'amazines'
    allowed_domains = ['amazines.com']
    start_urls = ['http://amazines.com/']

    def parse(self, response):
        pass

# -*- coding: utf-8 -*-
import scrapy
import re
import w3lib.html

class EzinearticlesSpider(scrapy.Spider):
    name = 'ezinearticles'
    start_urls = ['https://ezinearticles.com/']

    #This website wants me to be a human so we do this....
    custom_settings = {
        'DOWNLOAD_DELAY': '5.0'
    }


    def parse(self, response):
        category_links = response.css("#categories li > .sub-menu li > a::attr(href)").getall()

        for link_a in category_links:
            yield response.follow(link_a, self.enter_article, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,'referer':'https://www.google.com/'})


    def enter_article(self, response):
        article_links = response.css(".article-title-link::attr(href)").getall()

        for link_a in article_links:
            yield response.follow(link_a, self.extract_article, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,'referer':'https://www.google.com/'})

    def extract_article(self, response):
        #Article info
        article_title = response.css("meta[property='og:title']::attr(content)").get()
        article_author = response.css(".by-line a::text").get()
        airticle_date = response.css("meta[property='og:article:published_time']::attr(content)").get()
        article_category = response.css("meta[property='og:article:section']::attr(content)").get()
        article_words = response.css(".meta-information .meta-information-container:nth-child(2)::text").get()
        article_summary = response.css("meta[name='description']::attr(content)").get()
        article_body = response.css("#article-content").getall()
        
        #Stuff we want to filter out
        white_space = w3lib.html.HTML5_WHITESPACE
        filter = f"\r|\n|\t|\r\n|{white_space}"

        #Filtering article_words
        filtered_one = re.sub(filter, "", article_words)
        article_words = re.sub("\"", "\'", filtered_one)

        #Filtering article_summary
        filtered_one = re.sub(filter, "", article_summary)
        article_summary = re.sub("\"", "\'", filtered_one)
        
        #Filtering article_body
        filtered_one = re.sub(filter, "", article_body)
        filtered_two = re.sub("\"", "\'", filtered_one)
        article_body = w3lib.html.remove_tags(filtered_two)

        #Site info
        encoding = response.css("meta[charset]::attr(charset)").get()
        origin = response.url.strip()
        site_name = response.css("meta[property='og:site_name']::attr(content)").get()

        #Other info
        html = response.css("#article-content").getall()
        image_url = response.css(".photo::attr(src)").get()

        #My json format
        yield {
            'article': {
                'title': article_title.strip(),
                'author': article_author.strip(),
                'pub_date': article_date.strip(),
                'word-count': int(article_words.strip()),
                'summary': article_summary.strip(),
                'body': article_body.strip(),
            },
            'article_secondary': {
                'category': article_category.strip(),
                'site-name': site_name.strip(),
                'images': {
                    'url': image_url.strip()
                }
            },
            'article_tertiary': {
                'html': html.strip(),
                'origin': origin.strip(),
                'encoding': encoding.strip()
            }
        }



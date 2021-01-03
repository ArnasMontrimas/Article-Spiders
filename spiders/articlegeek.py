# -*- coding: utf-8 -*-
import scrapy
import re

class ArticlegeekSpider(scrapy.Spider):
    #Spider name
    name = 'articlegeek'

    #Strating url for spider   
    start_urls = ['http://www.articlegeek.com/']

    def parse(self, response):
        category_links = response.css("p.categories")

        #This gets me all the category links(hrefs)
        for link in category_links:
            for link_a in link.css("a::attr(href)"):
                #Will enter each link and run a callback function
                yield response.follow(link_a.get(), self.enter_article)

    #This function will enter each article inside a category
    def enter_article(self, response):
        article_links = response.css("#content > div p")

        for link in article_links:
            for link_a in link.css("a::attr(href)"):
                #Will enter each link and run a callback function
                yield response.follow(link_a.get(), self.extract_article)


    #This function will extract data from the article
    def extract_article(self, response):
        heading = response.css("div[id='content'] h1::text").get()
        author = response.css("div.author").css("a::text").get()
        main_content = response.css("div[id='content']").css("div.author ~ p:not(p[align='center'])")

        byline = "ArticleGeek"
        body = ""
        joined = ""

        for p_tag in main_content:
            #Stop looping through sibling tags when we reach a certain tag (They way i figure out when to stop is checking what is inside the tag and if criteria matched we stop)
            if p_tag.css("strong::text").get() != None:
                if p_tag.css("strong::text").get() == "Author Bio":
                    break
            if p_tag.css("em::text").get() != None:
                if p_tag.css("em::text").get() in 'Article Source: <a href="http://www.articlegeek.com">http://www.ArticleGeek.com - Free Website Content</a>':
                    break
            #Construct body
            body = p_tag.getall()
            string = ""
            joined += string.join(body)

        #Format body
        filtered = re.sub('(<p>|</p>|<strong>|</strong>|<a.*?</a>|<sup>|</sup>|<u>|</u>|href=|<ul>|</ul>|<li>|</li>|<ol>|</ol>|<em>|</em>|<br>|\r|\n|\t|\r\n)', '', joined)

        #If Output is CSV you dont need this
        filtered = re.sub("\"", '\'', filtered)
        body_text = filtered

        #Check that author is not None
        if author == None:
            author = "No Author"

        #My json format (Add WORD COUNT SO USE PYTHON TO COUNT WORDS.....)
        yield {
            'heading': heading.strip(),
            'author': "By: "+author.strip(),
            'word-count': len(body_text.split()),
            'body': body_text.strip(),
            'byline': byline.strip(),
            'origin': response.url.strip()
        }


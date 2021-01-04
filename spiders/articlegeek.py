# -*- coding: utf-8 -*-
import scrapy
import re
import w3lib.html

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
        encoding = "ISO-8859-1"
        category = response.css("#content > a:nth-child(3)::text").get()
        description = response.css("head > meta[name='Description']::attr(content)").get()

        if description == None:
            description = ""

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

        #Html5 White Space
        white_space = w3lib.html.HTML5_WHITESPACE

        #The filter
        filter = f"\r|\n|\t|\r\n|{white_space}"
        
        #filter out escaped characters
        filtered = re.sub(filter, "", joined)

        #Change double quotes to single quotes
        filtered = re.sub("\"", "\'", filtered)
        
        #Remove HTML tags
        body_text = w3lib.html.remove_tags(filtered)

        #Check that author is not None
        if author == None:
            author = "No Author"

        #My json format
        yield {
            'article': {
                'title': heading.strip(),
                'author': author.strip(),
                'pub_date': "",
                'word_count': len(body_text.split()),
                'summary': description.strip(),
                'body': body_text.strip()
            },
            'article_secondary': {
                'cateogry': category.strip(),
                'site_name': byline.strip(),
                'images': {
                    'url': ""
                },
            },
            'article_tertiary': {
                'html': joined.strip(),
                'origin': response.url.strip(),
                'encoding': encoding.strip()
            }
        }


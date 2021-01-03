# -*- coding: utf-8 -*-
import scrapy
import re
import w3lib.html

class ArticlefactirySpider(scrapy.Spider):
    #Spider name
    name = 'articlesfactory'

    #Starting url for spider
    start_urls = ['http://www.articlesfactory.com/all-categories.html']

    def parse(self, response):
        #Here i'm selecting a tr withing a table which contains all category links
        category_links = response.css("div.txt-main > table:nth-child(3) tr")

        #Now i loop through each 'tr'
        for link_tr in category_links:
            #Inside the table row there is a 'td' inside the 'td' there is 'a' tags with links to category pages
            #We select all of those 'a' tags withing the 'tr' loop through all of them
            for link_a in link_tr.css("a::attr(href)"):
                #Go to the next page on the next page we enter articles again and loop for 10 pages
                yield response.follow(link_a.get(), self.enter_article)


    def enter_article(self, response):
        #Here i'm selecting 'div.txt-main' tag which contains a tags with links to articles
        article_links = response.css("div.txt-main")

        #Here i'm looping through each link and enter it when i enter the link i run a function 'extract_article'
        for link_a in article_links.css("a.h2-center::attr(href)"):
            yield response.follow(link_a.get(), self.extract_article)

    
    def extract_article(self, response):
        article_heading = response.css("h1.h2::text").get()
        article_description = response.css("div.txt-main > div.bottom-link ~ p:nth-of-type(2)::text").get()
        article_author = response.css("a.small-link::text").get()
        article_category = response.css(".bottom-link > a:nth-child(1)::text").get()
        article_date = response.css(".bottom-link > a:nth-child(2)::text").get()
        byline = "articlesfactory"

        encoding = "iso-8859-1"

        #Some if statements to avoid erorrs if nothing found on certain pages that dont follow the same structure as others
        if article_description == None or article_description == "" or article_description == "<b></b>":
            article_description = response.css("div.txt-main > div.bottom-link ~ p:nth-of-type(1)::text").get()

        #If still nothing was found set description to none
        if article_description == None or article_description == "" or article_description == "<b></b>":
            article_description = "No Description"

        #Now lets get the main text of the article
        main_p_tags = response.css("div.txt-main table:nth-of-type(2) ~ p")

        #Article body final form
        body = ""
        joined = ""

        for p_tag in main_p_tags:
            #Now when we reach a tag with this class name we are done with the article body and stop
            if p_tag.xpath("@class").get() == "txt-small-regular":
                break
            #Construct article body
            body = p_tag.getall()
            string = ""
            joined += string.join(body)

        white_space = w3lib.html.HTML5_WHITESPACE

        filter = f"\r|\n|\t|\r\n|{white_space}"
        #filter out escaped characters
        filtered = re.sub(filter, "", joined)

        #Change double quotes to single quotes
        filtered = re.sub("\"", "\'", filtered)
        
        #Remove HTML tags
        article_body = w3lib.html.remove_tags(filtered)
        
        #Break out of recursive function if empty body text or word count for article ends up being 0
        if article_body == "" or len(article_body.split()) == 0:
            return None

        #My json format (Add WORD COUNT SO USE PYTHON TO COUNT WORDS...)
        yield {
            'article': {
                'title': article_heading.strip(),
                'author': article_author.strip(),
                'pub_date': article_date.strip(),
                'word-count': len(article_body.split()),
                'summary': article_description.strip(),
                'body': article_body.strip(),
            },
            'article_secondary': {
                'category': article_category.strip(),
                'site_name': byline.strip(),
                'images': {
                    'url': None
                }
            },
            'article_tertiary': {
                'html': joined.strip(),
                'origin': response.url.strip(),
                'encoding': encoding
            },
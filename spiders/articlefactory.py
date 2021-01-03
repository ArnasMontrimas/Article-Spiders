# -*- coding: utf-8 -*-
import scrapy
import re

class ArticlefactirySpider(scrapy.Spider):
    #Spider name
    name = 'articlefactiry'

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
                #Now enter each link when we enter it inside the link we run a function 'enter-article'
                yield response.follow(link_a.get(), self.enter_article)

    def enter_article(self, response):
        #Here i'm selecting 'div.txt-main' tag which contains a tags with links to articles
        article_links = response.css("div.txt-main")

        #Here i'm looping through each link and enter it when i enter the link i run a function 'extract_article'
        for link_a in article_links.css("a.h2-center::attr(href)"):
            yield response.follow(link_a.get(), self.extract_article)
            
        #TODO This will only enter articles on the first page (We want to enter articles up to 10 pages (Leaving this for later))
    def extract_article(self, response):
        article_heading = response.css("h1.h2::text").get()
        article_description = response.css("div.txt-main > div.bottom-link ~ p:nth-of-type(2)::text").get()
        article_author = response.css("a.small-link::text").get()
        byline = "ArticleFactory"

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

        #Format the body
        filtered = re.sub('(<p>|</p>|<strong>|</strong>|<a.*?</a>|<sup>|</sup>|<u>|</u>|href=|<ul>|</ul>|<li>|</li>|<ol>|</ol>|<em>|</em>|<br>|\r|\n|\t|\r\n)', '', joined)

        #If Output is CSV you dont need this
        filtered = re.sub("\"", "\'", filtered)
        article_body = filtered

        #Break out of recursive function if empty body text or word count for article ends up being 0
        if article_body == "" or len(article_body.split()) == 0:
            return False

        #My json format (Add WORD COUNT SO USE PYTHON TO COUNT WORDS...)
        #TODO ADD DATE OF THE ARTICLE!!!
        yield {
            'heading': article_heading.strip(),
            'author': article_author.strip(),
            'description': article_description.strip(),
            'word-count': len(article_body.split()),
            'body': article_body.strip(),
            'byline': byline.strip(),
            'origin': response.url.strip()
        }

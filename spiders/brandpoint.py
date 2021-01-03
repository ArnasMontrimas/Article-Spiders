# -*- coding: utf-8 -*-
import scrapy
import re

class BrandpointSpider(scrapy.Spider):
    #Spider name
    name = 'brandpoint'
    
    #Starting ulr for spider
    start_urls = ['https://www.brandpointcontent.com//']

    def parse(self, response):
        category_links = response.css("div.col-md-4 div.row div.col-md-12 div.row div")

        #This gets me all the category links(hrefs)
        for link in category_links:
            for link_a in link.css("a::attr(href)"):
                #This prints out all the href links
                #print(link_a.get())
                yield response.follow(link_a.get(), self.enter_article)

    #This is a function that will enter each article inside a category
    def enter_article(self, response):
        #Get all the article rows
        article_rows = response.css("div.col-md-10 div.row")
        #Loop through each article row
        for row in article_rows:
            #Inside each article row we get all the cards
            columns = row.css("div.col-md-4")
            #Loop through each card getting its link
            for article in columns:
                article_link = article.css("div a::attr(href)").get()
                yield response.follow(article_link, self.extract_article)


    #This method is for extracting content from article
    def extract_article(self, response):
        #The heading and body of article
        heading = response.css(".container > .row:nth-child(1)")
        body = response.css(".container > .row:nth-child(2)")
        
        #Heading subdivided into individual components
        article_heading = heading.css("div h1::text").get()
        posted_on = heading.css("div span.mr-2::text").get()
        word_count = heading.css("div span.ml-2::text").get()
        

        #Body subdivided into individual components
        img_src = body.css("div.col-md-9 > div:nth-child(1) img::attr(src)").get()
    
        #Format the body text
        body_text_para = body.css("div.col-md-9 > div.mt-4 p").getall()
        string = ""
        joined = string.join(body_text_para)
        filtered = re.sub('(<p>|</p>|<strong>|</strong>|<a.*?</a>|<sup>|</sup>|<u>|</u>|href=|<ul>|</ul>|<li>|</li>|<ol>|</ol>|<em>|</em>|<br>)', '', joined)
        
        #If Output is CSV you dont need this
        filtered = re.sub('"','\'', filtered)
        article_text = filtered

        byline = "Brandpoint" #Basically who made this artice (must be encluded for legal reasons)

        #My json format
        yield {
            'heading': article_heading.strip(),
            'date': posted_on.strip(),
            'words': word_count.strip(),
            'image': img_src.strip(),
            'body': article_text.strip(),
            'byline': byline.strip(),
            'origin': response.url.strip()
        }



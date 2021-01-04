# -*- coding: utf-8 -*-
import scrapy
import re
import w3lib.html

class BrandpointSpider(scrapy.Spider):
    #Spider name
    name = 'brandpoint'
    
    #Starting ulr for spider
    start_urls = ['https://www.brandpointcontent.com//']

    #Article categories
    article_category = ""

    def parse(self, response):
        category_links = response.css("div.col-md-4 div.row div.col-md-12 div.row div")

        #This gets me all the category links(hrefs)
        for link in category_links:
            for link_a in link.css("a::attr(href)"):
                #Get the category which we are currently in
                self.article_category = re.sub("/|category", "", link_a.get())
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
        
        #Char set
        encoding = response.css("head > meta[charset]::attr(charset)").get()

        #Description
        article_description = response.css("head > meta[name='description']::attr(content)").get()

        if(article_description == None):
            article_description = ""

        #Body subdivided into individual components
        img_src = body.css("div.col-md-9 > div:nth-child(1) img::attr(src)").get()
    
        #Format the body text
        body_text_para = body.css("div.col-md-9 > div.mt-4 p").getall()
        string = ""
        joined = string.join(body_text_para)

        #Html5 White Space
        white_space = w3lib.html.HTML5_WHITESPACE

        #The filter
        filter = f"\r|\n|\t|\r\n|{white_space}"
        
        #filter out escaped characters
        filtered = re.sub(filter, "", joined)

        #Change double quotes to single quotes
        filtered = re.sub("\"", "\'", filtered)
        
        #Remove HTML tags
        article_text = w3lib.html.remove_tags(filtered)

        byline = "Brandpoint" #website which website is on (must be encluded for legal reasons)

        #My json format
        yield {
            'article': {
                'title': article_heading.strip(),
                'author': "BrandPoint",
                'pub_date': posted_on.strip(),
                'word_count': word_count.strip(),
                'summary': article_description.strip(),
                'body': article_text.strip(),
            },
            'article_secondary': {
                'cateogry': self.article_category.strip(),
                'site_name': byline.strip(),
                'images': {
                    'url': img_src.strip()
                },
            },
            'article_tertiary': {
                'html': joined.strip(),
                'origin': response.url.strip(),
                'encoding': encoding.strip()
            }
        }



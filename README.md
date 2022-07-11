## About
#### Article Scraping (Scrapy Spiders) (ABADONED)
This project was started out of curiosity for web scraping, after searching online how to do web scraping with php, javascript i didnt really like what they had to offer and landed on python with scrapy which seemed to have good documentation ease of use (compared to others) and alot of functionallity.

I have created 4 spiders, each spider crawls 1 website, the spiders first retrieve all category links, they then follow those categories enter all articles (On the first page, which ussualy are the most recent ones) and extract the article, the information wich i get is: title,author,publication date,word count,summary,body,category,images,original link to article. Some of the information is not always present so i simply subsitute with null value.
Secondary information which i get is, raw html of the article, site name, encoding.

I have learned some recurssion, python and more on css-selectors.

This project is still ongoing my final plan for the project is to scrape as many Copyright free article websites as i cann, store them all in 1 place and create api endpoins which can be used to retrieve articles by name,category,word-count,date.
I also plan to have the crawlers run every 2 or 3 days to keep the articles up to date and remove articles which are older than 1 month.


## Functionality
* Crawl Websites
* Export Data to Json or Excel

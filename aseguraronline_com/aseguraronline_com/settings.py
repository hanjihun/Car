# -*- coding: utf-8 -*-

# Scrapy settings for aseguraronline_com project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'aseguraronline_com'

SPIDER_MODULES = ['aseguraronline_com.spiders']
NEWSPIDER_MODULE = 'aseguraronline_com.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'aseguraronline_com (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
   'aseguraronline_com.middlewares.selenium_middleware.SeleniumMiddleware': 1,
}

PHANTOMJS_PATH = "./../phantomjs.exe"

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 0.5
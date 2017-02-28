# -*- coding: utf-8 -*-

# Scrapy settings for asegurarmiauto_com project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'asegurarmiauto_com'

SPIDER_MODULES = ['asegurarmiauto_com.spiders']
NEWSPIDER_MODULE = 'asegurarmiauto_com.spiders'


USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')
COOKIES_ENABLED = False

#CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 0.9

# DOWNLOADER_MIDDLEWARES = {
#    'asegurarmiauto_com.middlewares.selenium_middleware.SeleniumMiddleware': 1,
# }

PHANTOMJS_PATH = "./../phantomjs.exe"
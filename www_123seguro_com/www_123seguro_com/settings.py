# -*- coding: utf-8 -*-

# Scrapy settings for _123seguro_com project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'www_123seguro_com'

SPIDER_MODULES = ['www_123seguro_com.spiders']
NEWSPIDER_MODULE = 'www_123seguro_com.spiders'

CONCURRENT_REQUESTS_PER_DOMAIN = 1
#DOWNLOAD_DELAY = 0.5

DOWNLOAD_TIMEOUT = 60

# DOWNLOADER_MIDDLEWARES = {
#    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
# }

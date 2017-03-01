# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest
from datetime import date
from collections import OrderedDict
from json import loads
import re, collections
from scrapy.utils.response import open_in_browser

class SeguruComArSpider(scrapy.Spider):

	name = "seguru_com_ar_spider"
	start_urls = ['http://www.seguru.com.ar/']
	

	def __init__(self, categories=None, *args, **kwargs):
		super(SeguruComArSpider, self).__init__(*args, **kwargs)
		#pass
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		self.sub_urls = loads(self.categories).keys()

	headers = {}
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	headers['X-Requested-With']='XMLHttpRequest'
	def parse(self, response):
		url = "http://www.seguru.com.ar/client_queries/get_agencies"

		for param in self.sub_urls:
		
			formdata = {}
			formdata['_method'] = 'POST'
			formdata['data[ClientQuery][brand]'] = param.split('---')[2]
			formdata['data[ClientQuery][year]'] = param.split('---')[4]
			formdata['data[ClientQuery][model]'] = param.split('---')[3]
			formdata['data[ClientQuery][province]'] = param.split('---')[-2]
			formdata['data[ClientQuery][locality]'] = param.split('---')[-1]
			formdata['data[ClientQuery][gender]'] = 'f'
			formdata['data[ClientQuery][age]'] = param.split('---')[6]
			formdata['data[ClientQuery][submit]'] = 'query_and_save'

			yield FormRequest(url, self.parse_agencies, method="POST", formdata=formdata, headers=self.headers, meta={'param':param})

	def parse_agencies(self, response):
		
		agencies = response.xpath('//*[contains(@id,"agency-")]/@data-url').extract()
		for agency in agencies:
			print agency
			yield Request(response.urljoin(agency), self.get_detail, headers=self.headers, meta={'param':response.meta['param']})


	def get_detail(self, response):
		agency_name = response.xpath('//*[@class="agency-plans-details"]/div/div[1]/img/@alt').extract_first()
		param = response.meta['param']
		types = response.xpath('//*[@class="agency-plans-details"]/div')
		for type in types:
			type_title = type.xpath('./div[2]/div/strong/text()').extract_first()
			price = type.xpath('./div[3]//text()').re('[\d.,]+')
			if price:
	# AUDI---RS4*4.2*V8*QUATTRO---9---620---14---2007---40---Buenos*Aires---ISLA*MACIEL---2---4020

				item = OrderedDict()
				item['Vendedor'] = 434
				item['Model'] = param.split('---')[1].replace('*',' ')
				item['Brand'] = param.split('---')[0].replace('*',' ')
				item['Year'] =  param.split('---')[5]
				item['Location'] = param.split('---')[-4].replace('*',' ') + " " + param.split('---')[-3].replace('*',' ')
				item['Age'] = param.split('---')[-5]
				item['Date'] = date.today()
				item['Company'] = agency_name
				item['Insurance Type'] = type_title
				item['Price'] = price[0].replace('.','').replace(',','.')
				item['Currency'] = "ARS"
				yield item

	def parse_detail(self, response):
		print response.meta['param'].split('---')[7],response.meta['times']
		if response.xpath('//script') or response.xpath('//table[@id="table"]//tr[@class=""]/td//text()').re('[\d.,]+') or response.meta['times'] > 20:
			
			if response.meta['times'] < 20:
				
				yield Request(response.url, callback=self.parse_detail, meta={'times':100, 'param':response.meta['param']},dont_filter=True)
			else:
				types = response.xpath('//table[@id="table"]//tr[@id="coberturas"]/td/p[1]/text()').extract()
				#print types
				companies = response.xpath('//table[@id="table"]//tr[@class=""]')
				
				for company in companies:
					# print company.xpath('./th/img/@src').extract_first()
					# continue
					company_name = company.xpath('./th//img/@src').extract_first().split('/')[-1].split('.')[0].title()

					prices = company.xpath('./td')
					#print company_name, len(prices)
					for index, price in enumerate(prices):
						price_val = price.xpath('.//text()').re('[\d.,]+')
						if price_val:
							# CHEVROLET---AGILE*1.4*LS*L/14---2013---40---12---56---120360---LA*PAMPA---LOS*OLIVOS---2---18385
							#print company_name, types[index], price_val[0].replace('.','').replace(',','.')
							param = response.meta['param']
							item = OrderedDict()
							item['Vendedor'] = 433
							item['Model'] = param.split('---')[1].replace('*',' ')
							item['Brand'] = param.split('---')[0].replace('*',' ')
							item['Year'] =  param.split('---')[2]
							item['Location'] = param.split('---')[-4].replace('*',' ') + " " + param.split('---')[-3].replace('*',' ')
							item['Age'] = param.split('---')[3]
							item['Date'] = date.today()
							item['Company'] = company_name
							item['Insurance Type'] = types[index]
							item['Price'] = price_val[0].replace('.','').replace(',','.')
							item['Currency'] = "ARS"
							yield item
		else:			
			yield Request(response.url, callback=self.parse_detail, meta={'times':response.meta['times']+1, 'param':response.meta['param']},dont_filter=True)
		



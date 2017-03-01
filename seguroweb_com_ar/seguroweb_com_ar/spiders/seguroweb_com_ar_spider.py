# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest
from datetime import date
from collections import OrderedDict
from json import loads
import re, collections

class SegurowebComArSpider(scrapy.Spider):

	name = "seguroweb_com_ar_spider"
	start_urls = ['http://seguroweb.com.ar/autos/']
	

	def __init__(self, categories=None, *args, **kwargs):
		super(SegurowebComArSpider, self).__init__(*args, **kwargs)
		#pass
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		self.sub_urls = loads(self.categories).keys()


	# CHEVROLET---AGILE*1.4*LS*L/14---2013---40---12---56---120360---LA*PAMPA---LOS*OLIVOS---2---18385
	
	def parse(self, response):
		url = "http://seguroweb.com.ar/autos/auto.php"

		for param in self.sub_urls:
			formdata = {}
			formdata['CLINOMBRE'] = "ANONIMO"
			formdata['CLIMAIL'] = "VENTASAUTO@SEGUROWEB.COM.AR"
			formdata['CLITEL'] = "44444444"
			formdata['marca'] = param.split('---')[4]
			formdata['version'] = param.split('---')[5]
			formdata['modelo'] = param.split('---')[6]
			formdata['anio'] = param.split('---')[2]
			formdata['CLIEDAD'] = param.split('---')[3]
			formdata['provincia'] = param.split('---')[-2]
			formdata['localidad'] = param.split('---')[-1]

			yield FormRequest(url, self.parse_car, formdata=formdata, method="POST", meta={'param':param})

	def parse_car(self, response):
		WkInstancia = response.xpath('//input[@name="WkInstancia"]/@value').extract_first()
		marca_auto = response.xpath('//input[@name="marca_auto"]/@value').extract_first()
		modelo_auto = response.xpath('//input[@name="modelo_auto"]/@value').extract_first().strip()
		AUANOFAB = response.xpath('//input[@name="AUANOFAB"]/@value').extract_first()
		PROVINCIA = response.xpath('//input[@name="PROVINCIA"]/@value').extract_first()
		CLIPLOC = response.xpath('//input[@name="CLIPLOC"]/@value').extract_first()
		CLIEDAD = response.xpath('//input[@name="CLIEDAD"]/@value').extract_first()
		WkInstancia = response.xpath('//input[@name="WkInstancia"]/@value').extract_first()

		url = "http://seguroweb.com.ar/autos/webservice.php"

		username = "sdfsdf"
		email = "info_info@gmail.com"
		phone = "55533444"
		query = "?action=1&dat1={}&dat2={}&dat3={}&dat4=011&dat5={}&dat6={}&dat7={}&dat8={}&dat9={}&dat10={}&dat11={}&dat12=http://seguroweb.com.ar/autos/&dat13=&dat14=&dat15="\
			.format(WkInstancia, username, email, phone, marca_auto, modelo_auto, AUANOFAB, PROVINCIA, CLIPLOC, CLIEDAD)
		
		#yield FormRequest(url+query, self.parse_detail, method="POST", formdata=formdata)
		
		yield Request(url+query, self.parse_detail, meta={'times':0, 'param':response.meta['param']})			
		
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
		



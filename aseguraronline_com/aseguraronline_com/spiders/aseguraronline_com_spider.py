# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest
from re import compile as recompile
from urlparse import urlparse
from json import loads
from datetime import date
import json
import datetime, time
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
class AseguraronlineComSpider(scrapy.Spider):

	name = "aseguraronline_com_spider"
	#start_urls = ['http://www.aseguraronline.com/seguros-para-autos/']
	#start_urls = ['http://webpack.wokan.com.ar/app/v1/auto/index.html']
	use_selenium = True
	# headers = {}
	# headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
	# headers['X-Wokan-Webpack-SID'] = "asegurarmiauto"

	def __init__(self, categories=None, *args, **kwargs):
		super(AseguraronlineComSpider, self).__init__(*args, **kwargs)
		#pass
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		
		self.sub_urls = loads(self.categories).keys()

	'''
	brand_name	model_name	brand_id	model_id	year
	ACURA	LEGEND  LS COUPE	1	5206	1997
	TOYOTA---COROLLA*1.8*XRS---129---2828---2014

	'''
	def start_requests(self):
		for param in self.sub_urls:
		#url = "http://www.aseguraronline.com/seguros-para-autos/resultado.php#/seguro-para-autos/cotizar/resultado?
		#marca=129&modelo=2828&anio=2014&cp=1284&nombre=apollo&edad=40&email=bbanzzakji@gmail.com&telefono=(0011)%205555-4444&lenguaje=es-AR"
		#TOYOTA---129---COROLLA*1.8*XRS---2828---2014---40---LA*PAMPA---LOS*OLIVOS---8203
			marca = param.split('---')[1]
			modelo = param.split('---')[3]
			anio = param.split('---')[4]
			cp = param.split('---')[-1]
			base_url = "http://www.aseguraronline.com/seguros-para-autos/resultado.php#/seguro-para-autos/cotizar/resultado?"
			queries = "marca={}&modelo={}&anio={}&cp={}&nombre=apollo&edad=40&email=info_tower@gmail.com&telefono=(0011)%205555-4444&lenguaje=es-AR".\
					format(marca, modelo, anio, cp)

			yield Request(base_url+queries, callback=self.parse, meta={'param':param}, dont_filter=True)
###########################################################


	def parse(self, response):
		param = response.meta['param']
		marca = param.split('---')[0]
		modelo = param.split('---')[2].replace('*',' ')
		anio = param.split('---')[4]

		types = response.xpath('//*[@class="file_titles"]/li//text()').extract()
		insarances = response.xpath('//*[@class="grid_block"]/div')

		companies = ['None','Sura', 'INTEGRITY', 'Unknown', 'Meridional SEGUROS', 'Provincia Seguros', 'QBE', 'MAPFRE', 'SMG SEGUROS']
		#print len(insarances)
		for ins in insarances:
			company_id = ''.join(ins.xpath('./div[1]/img/@src').extract()).split('_')[-1].split('.')[0]			
			prices = ins.xpath('./ul/li//*[@class="price ng-binding"]/text()').extract()

			for index, price in enumerate(prices):
				p = price.replace('$','').strip()
				if p != "0":
					item = OrderedDict()
					item['Model'] = modelo
					item['Brand'] = marca
					item['Year'] = anio
					item['Location'] = param.split('---')[-3] + " " + param.split('---')[-2]
					item['Age'] = "40"
					item['Date'] = date.today()
					item['Company'] = companies[int(company_id)]
					item['Insurance Type'] = types[index]
					item['Price'] = p
					print item
					yield item
			

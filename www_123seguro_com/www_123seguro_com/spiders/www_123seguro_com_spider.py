# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest

from urlparse import urlparse
from json import loads
from datetime import date
import json, re
import datetime, time
from scrapy.utils.response import open_in_browser
from collections import OrderedDict

class Www123SeguroComSpider(scrapy.Spider):

	name = "www_123seguro_com_spider"
	start_urls = ['https://www.123seguro.com/']

	#custom_settings = {'DOWNLOAD_DELAY' : 10}

	company_list = ['1','2','3','4','5','6','7','9','13','14','1001','1002']



	def __init__(self, categories=None, *args, **kwargs):
		super(Www123SeguroComSpider, self).__init__(*args, **kwargs)
		#pass
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		
		self.sub_urls = loads(self.categories).keys()


	def start_requests(self):
		for param in self.sub_urls:
			# "param" looks like below
			# 450285---TOYOTA---YARIS*CVT---2016---40---LA*PAMPA---LOS*OLIVOS---8203---20652

			for company_id in self.company_list:

				ts = int(round(time.time() * 1000))
				url = "https://api3.123seguro.com/cotizar?"
				query = "callback=jQuery110207711256416726426_{}&riesgo=1&compania={}&canal=1&productor=2&producto%5Bvehiculo_id%5D={}&producto%5Banio%5D={}&producto%5Buso_v%5D=1&usuario%5Blocalidad_id%5D={}&usuario%5Bedad%5D=40&_={}".\
					format(str(ts), company_id, param.split('---')[0], param.split('---')[3], param.split('---')[-1], str(ts+1))

				info = {}
				info['model_name'] = param.split('---')[2].replace('*',' ')
				info['marca_name'] = param.split('---')[1].replace('*',' ')
				info['year'] = param.split('---')[3]
				info['age'] = param.split('---')[4]

				yield Request(url+query, callback=self.parse_price, meta={'info':info, 'param':param})




	### Iterate all brand/version/model and yield the requests from the infor.
	
	def parse(self, response):
		marca_data = json.loads(response.xpath('//*[@id="data-marcas"]/text()').extract_first())

		for index, marca in enumerate(marca_data):
			if index == 0:
				continue
			#print marca['nombre'], marca['id']
			url = "https://www.123seguro.com/vehiculo/front/auto/familias?queries%5B%5D=familia.marca_id%3D{}".format(marca['id'])
			yield Request(url, callback=self.parse_marca, meta={'info':{'marca_id':marca['id'], 'marca_name':marca['nombre']}})
			

	def parse_marca(self, response):
		versions = json.loads(response.body)
		info = response.meta['info']
		for ver in versions:
			print ver['nombre'], ver['id']
			info1 = {}
			info1['version_id'] = ver['id']
			info1['version_name'] = ver['nombre']
			url = "https://www.123seguro.com/vehiculo/front/auto/modelos?queries%5B%5D=familia_id%3D{}&queries%5B%5D=modelo.marca_id%3D{}".format(ver['id'],info['marca_id'])
			info1.update(info)
			yield Request(url, callback=self.parse_version, meta={'info':info1})
			

	def parse_version(self, response):
		models = json.loads(response.body)

		info = response.meta['info']
		
		for model in models:
			print model['nombre'], model['id']
			info1 = {}
			info1['model_id'] = model['id']
			info1['model_name'] = model['nombre']
			info1['age'] = 40
			info1.update(info)
			url = "https://www.123seguro.com/vehiculo/front/auto/anios?queries%5B%5D=modelo.id%3D{}".format(model['id'])
			yield Request(url, callback=self.parse_model, meta={'info':info1})


				

	def parse_model(self, response):
		years = json.loads(response.body)

		info = response.meta['info']
		for year in years:
			if year['anio_real'] == "0":
				continue

			info1 = {'year':year['anio_real']}
			info1.update(info)

			print info['model_name'], year['anio'], year['anio_real']

			
			# Make the brand/version/model list to fetch model id.
			# yield OrderedDict({'brand':info['marca_name'], 'version':info['version_name'], 'model':info['model_name'],'model_id':info['model_id'], 'year':year['anio_real'], 'age':'40'})
			# 

			for param in self.sub_urls:					
				location_id = param.split('---')[-1]

				for company_id in self.company_list:

					ts = int(round(time.time() * 1000))
					url = "https://api3.123seguro.com/cotizar?"
					query = "callback=jQuery110207711256416726426_{}&riesgo=1&compania={}&canal=1&productor=2&producto%5Bvehiculo_id%5D={}&producto%5Banio%5D={}&producto%5Buso_v%5D=1&usuario%5Blocalidad_id%5D={}&usuario%5Bedad%5D=40&_={}".\
						format(str(ts), company_id, info['model_id'], year['anio_real'], location_id, str(ts+1))

					yield Request(url+query, callback=self.parse_price, meta={'info':info1, 'param':param})

			#break


	def parse_price(self, response):
		param = response.meta['param']
		data = re.findall('jQuery\d+_\d+\((.*)\);', response.body)
		info = response.meta['info']
		if data:
			result = json.loads(data[0])
			try:
				if result['error']:
					print "Nothing"
				
			except:
				print "Found prices from ",info['model_name'],"model for ", result['compania'], "company."

				types = {"8":"Responsabilidad Civil", "4":"Terceros Completos", "5":"Terceros Completos Full", "6":"Terceros Completos Full + Granizo", "7":"Todo Riesgo"}
				price_info = result['precios']

				location = param.split('---')[-4].replace('*',' ') + param.split('---')[-3].replace('*',' ')
				location = location + " (" + param.split('---')[-2] + ")"

				for ins_type in types.keys():
					item = OrderedDict()
					item['model'] = info['model_name']
					item['brand'] = info['marca_name']
					item['year'] = info['year']
					item['location'] = location
					item['age'] = info['age']
					item['date'] = date.today()
					item['company'] = result['compania']
					item['insurance type'] = types[ins_type]
					item['price'] = ""
					try:
						price = price_info[ins_type]['premio'][price_info[ins_type]['premio'].keys()[0]]
						print "Price ===== ", price						
						
						item['price'] = price
						#item['url'] = response.url
						yield item
					except:
						pass
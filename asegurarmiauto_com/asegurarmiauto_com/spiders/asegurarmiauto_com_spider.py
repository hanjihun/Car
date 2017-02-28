# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest
from re import compile as recompile
from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict
import json
import datetime, time

class AsegurarmiautoComSpider(scrapy.Spider):

	name = "asegurarmiauto_com_spider"
	start_urls = ['http://www.asegurarmiauto.com/']
	#start_urls = ['http://webpack.wokan.com.ar/app/v1/auto/index.html']
	use_selenium = False
	

	def __init__(self, categories=None, *args, **kwargs):
		super(AsegurarmiautoComSpider, self).__init__(*args, **kwargs)

		self.use_selenium = False
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		
		self.sub_urls = loads(self.categories).keys()

###########################################################

	# def start_requests(self):
	# 	yield Request(self.start_urls[0], callback=self.parse)

	def parse(self, response):
		time.sleep(3)
		for param in self.sub_urls:
			#TOYOTA---YARIS*CVT---2016---450285---40---LA*PAMPA---LOS*OLIVOS---8203
			year = param.split('---')[4]
			birth = datetime.datetime.now() - datetime.timedelta(days=365*int(year)) # 40 years old
			formdata = {}
			formdata['anio'] = param.split('---')[2]
			formdata['codigo_postal'] = param.split('---')[-1]
			formdata['email'] = "info_tower@gmail.com"
			formdata['es_cero'] = "0"
			formdata['estado_civil'] = "casado"
			formdata['fecha_nacimiento'] = birth.strftime('%Y-%m-%d')
			formdata['infoauto_codigo'] = param.split('---')[3]
			formdata['nombre'] = "bbanzzakji"
			formdata['sexo'] = "m"
			formdata['tel_area'] = "011"
			formdata['tel_numero'] = "55554444"
			formdata['tiene_gnc'] = "0"
			formdata['tiene_rastreador'] = "0"
			print formdata

			headers = {}
			headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
			headers['X-Wokan-Webpack-SID'] = "asegurarmiauto"
			headers['Content-Type'] = "application/json;charset=UTF-8"
			headers['Accept'] = "application/json, text/plain, */*"
			headers['Accept-Encoding'] = "gzip, deflate"
			headers['Accept-Language'] = "en-US,en;q=0.8"
			headers['Connection'] = "keep-alive"

			yield Request('http://webpack.wokan.com.ar/api/v1/autos/cotizacion', callback=self.parse1, body=json.dumps(formdata), method="POST", headers=headers, meta={'param':param})
			

	def parse1(self, response):
		url = "http://webpack.wokan.com.ar/api/v1/autos/cotizacion/" + loads(response.body)['token']
		print url

		headers = {}
		headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
		headers['X-Wokan-Webpack-SID'] = "asegurarmiauto"
		headers['Content-Type'] = "application/json;charset=UTF-8"
		headers['Accept'] = "application/json, text/plain, */*"
		headers['Accept-Encoding'] = "gzip, deflate, sdch"
		headers['Accept-Language'] = "en-US,en;q=0.8"
		headers['Connection'] = "keep-alive"
		
			
		yield Request(url, callback=self.parse_data,  headers=headers, dont_filter=True, 
						meta={'hdr':headers, 'link':url, 'param':response.meta['param']})

	def parse_data(self, response):
		data = loads(response.body)
		bFinalized = True
		for c in data['aseguradoras']:
			if "iniciado" == c['cotizador']['estado']:
				bFinalized = False
				break

		if not bFinalized:	
			url = response.meta['link']
			headers = response.meta['hdr']
			
			yield Request(url, callback=self.parse_data,  headers=headers, dont_filter=True, 
							meta={'hdr':headers, 'link':url, 'param':response.meta['param']})
		else:
			for c in data['aseguradoras']:
				company_name = c['aseguradora_id']
				for p in c['cotizador']['coberturas']:
					insurance_type = p['cobertura']['nombre']
					price = p['premio']
					print company_name, insurance_type, price
					item = OrderedDict()
					param = response.meta['param']
					#TOYOTA---YARIS*CVT---2016---450285---40---LA*PAMPA---LOS*OLIVOS---8203
					item['Vendor'] = 432
					item['Brand'] = param.split('---')[0]
					item['Version'] = param.split('---')[1].replace('*',' ')
					item['Year'] = param.split('---')[2]
					item['Age'] = param.split('---')[4]
					item['Location'] = param.split('---')[5].replace('*',' ') + " " + param.split('---')[6].replace('*',' ')
					item['Company'] = company_name
					item['Insurance Type'] = insurance_type
					item['Date'] = date.today()
					item['Price'] = price
					item['Currency'] = "ARS"
					yield item
# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest
from datetime import date
from collections import OrderedDict
from json import loads
import re, collections, json
from scrapy.utils.response import open_in_browser

class Seguros911ComArSpider(scrapy.Spider):

	name = "seguros911_com_ar_spider"
	start_urls = ['https://www.seguros911.com.ar/']
	

	def __init__(self, categories=None, *args, **kwargs):
		super(Seguros911ComArSpider, self).__init__(*args, **kwargs)
		#pass
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		self.sub_urls = loads(self.categories).keys()

	headers = {}
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	headers['X-Requested-With']='XMLHttpRequest'

	companies = ['SMG', 'PROVINCIA', 'ORBIS', 'ALLIANZ', 'CALEDONIA', 'INTEGRITY', 'ZURICH', 'BOSTON']

	types = ['Resp.Civil', 'RC y Daños Totales', 'Todo Total', 'Terceros Completo', 'Terceros Completo Superior', 'Terceros Completo Premium', 'T.Riesgo c/ Franquicia',
			'T.Riesgo c/ Franq Plus', 'T.Riesgo c/ Franq Premium',]

	def parse(self, response):
		print "##"
		for param in self.sub_urls:
			for company in self.companies:
				#company = "ALLIANZ"
				url = "https://www.seguros911.com.ar/process/process_{}.php".format(company)

				#param = "TOYOTA---COROLLA*1.8*XLI**********L/08---2003---40---450159---Buenos*Aires,*Barrio*Parque*Leloir(1713)---1---1713---16447"

				formdata = {}
				formdata['anio'] = param.split('---')[2]#'2007'
				formdata['suma'] = '159000'
				formdata['infoautocod'] = param.split('---')[4]#'450154'
				formdata['es_cero'] = 'N'
				formdata['marca'] = param.split('---')[0]#'TOYOTA'
				formdata['prov_id'] = param.split('---')[-3]#'1'
				formdata['loc_id'] = param.split('---')[-1]#'16445'
				formdata['cp'] = param.split('---')[-2]#'1713'

				# formdata['id_marca'] = '45'
				# formdata['id_modelo'] = '8'
				# formdata['id_version']='154'
				# formdata['cliente_sexo'] = 'M'
				yield FormRequest(url, self.parse_details, method="POST", formdata=formdata, headers=self.headers, meta={'param':param, 'company':company})
			
	def parse_details(self, response):
		data = json.loads(response.body)
		company = response.meta['company']
		param = response.meta['param']

		if data['error'] == False:
			print "Sucess!!!"
			types = data['coberturas']
			for t in types.keys():
				info = types[t]
				try:
					price = info['precio']
					if str(price) != '0':
						#"TOYOTA---COROLLA*1.8*XLI**********L/08---2011---40---450159---Buenos*Aires,*Barrio*Parque*Leloir(1713)---1---1713---16447"
						print price, self.types[int(t) - 1]
						item = OrderedDict()					
						item['Vendedor'] = 435
						item['Model'] = param.split('---')[1].replace('*', ' ')
						item['Brand'] = param.split('---')[0]
						item['Year'] = param.split('---')[2]
						item['Location'] = param.split('---')[-4].replace('*', ' ')
						item['Age'] = param.split('---')[3]
						item['Date'] = date.today()
						item['Company'] = company
						item['Insurance Type'] = self.types[int(t) - 1]
						item['Price'] = price
						item['Currency'] = "ARS"
						yield item
				except:
					pass
		else:
			print "Error!!!"
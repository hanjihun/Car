# -*- coding: utf-8 -*-
import scrapy, json
from scrapy.exceptions import CloseSpider
from scrapy import Request
from json import loads
from datetime import date
from collections import OrderedDict


class SegurarseComArSpider(scrapy.Spider):

	name = "segurarse_com_ar_spider"

	#start_urls = ('https://segurarse.com.ar/cotizador-de-seguros-auto',)

	company_list = ['allianz','liberty','mapfre','mercantil','meridional','orbis','sancristobal','sancor','rsa','zurich',]
	ins_types = {'valA':'Responsabilidad Civil','valB':'Terceros Completos','valC':'Terceros Completos Full','valD':'Terceros Completos Full + Granizo','valE':'Todo Riesgo'}
	use_selenium = False

	def __init__(self, categories=None, *args, **kwargs):
		super(SegurarseComArSpider, self).__init__(*args, **kwargs)
		#pass
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		
		self.sub_urls = loads(self.categories).keys()



	# Combination sample:
	# brand / version / year / age / province / location / zip	
	# TOYOTA---LITE*ACE---1988---40---LA*PAMPA---LOS*OLIVOS---8203

	def start_requests(self):

		for param in self.sub_urls:
			for company in self.company_list:


				compania = company#"zurich"
				marca = param.split('---')[0].replace('*',' ')#"TOYOTA"
				anioNum = param.split('---')[2]#"2016"
				#esCeroKm = "False"
				#tieneAlarma = "False"
				provincia = param.split('---')[4].replace('*',' ')#"CAPITAL FEDERAL"
				localidad = param.split('---')[5].replace('*',' ')#"BELGRANO"
				version = param.split('---')[1].replace('*',' ')#"COROLLA 1.8 SE-G         L/14"
				codigoPostal = param.split('---')[-1]#"1428"
				#sumaAseguradaIA = "375.000,00"
				#codigoIA = "450245"
				edad = param.split('---')[3]#"35"
				gnc = "False"
				cobertura = "4"
				sexo="Masculino"

				url = "https://segurarse.com.ar/Service2/CotizarWEB"
				query = "compania={}&marca={}&anioNum={}&provincia={}&localidad={}&version={}&codigoPostal={}&edad={}&cobertura={}&sexo={}".\
					format(compania, marca, anioNum, provincia, localidad, version, codigoPostal, edad, cobertura, sexo)

				url = url + "?" + query.replace(' ','+')
				
				yield Request(url, callback=self.parse_products, meta={'param':param, 'company':company})		


	def parse_products(self, response):
		param = response.meta['param']

		value_list = json.loads(response.body)
		for value_key in value_list.keys():
			if value_list[value_key] == "-":
				continue

			item = OrderedDict()
			item['Vendedor'] = 428
			item['Model'] = param.split('---')[1].replace('*',' ')
			item['Brand'] = param.split('---')[0].replace('*',' ')
			item['Year'] = param.split('---')[2]
			item['Location'] = param.split('---')[4].replace('*',' ') + " " + param.split('---')[5].replace('*',' ')
			item['Age'] = param.split('---')[3]
			item['Date'] = date.today()
			item['Company'] = response.meta['company'].title()
			item['Insurance Type'] = self.ins_types[value_key]
			item['Price'] = value_list[value_key].replace('$','').replace('.','').replace(',','.')
			item['Currency'] = "ARS"

			yield item
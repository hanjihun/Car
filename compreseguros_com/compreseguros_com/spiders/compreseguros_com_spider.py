# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest, Selector

from datetime import date
from collections import OrderedDict
from json import loads
from random import randint

import json, re
import datetime, time

# Remove below package when publishing
from scrapy.utils.response import open_in_browser

class CompresegurosComSpider(scrapy.Spider):

	name = "compreseguros_com_spider"
	start_urls = ['https://www.compreseguros.com/']

	handle_httpstatus_list = [302]
	#custom_settings = {'DOWNLOAD_DELAY' : 10}

	# def __init__(self, categories=None, *args, **kwargs):
	# 	super(Www123SeguroComSpider, self).__init__(*args, **kwargs)
	# 	#pass
	# 	if not categories:
	# 		raise CloseSpider('Received no categories!')
	# 	else:
	# 		self.categories = categories
	# 	self.sub_urls = loads(self.categories).keys()


	def parse(self, response):

		url = "https://www.compreseguros.com/seguros-de-autos"

		formdata = {}
		formdata['cotizacion[infoauto_marca]'] = '12'
		formdata['cotizacion[anio]'] = '2016'
		formdata['cotizacion[infoauto_grupo]'] = '163'
		formdata['cotizacion[infoauto_codigo]'] = '120462'
		formdata['cotizacion[tiene_gnc]'] = '0'
		formdata['cotizacion[sexo]'] = 'm'
		formdata['cotizacion[estado_civil]'] = 'casado'
		formdata['cotizacion[email]'] = 'baduk@gmail.com'
		formdata['cotizacion[codigo_postal]'] = '1428'
		formdata['cotizacion[tel_area]'] = '011'
		formdata['cotizacion[tel_numero]'] = str(randint(50000000, 90000000))
		formdata['cotizacion[edad]'] = '40'
		formdata['cotizacion[_csrf_token]'] = response.xpath('//input[@id="cotizacion__csrf_token"]/@value').extract_first()

		yield FormRequest(url, self.send_information, method="POST", formdata=formdata, meta={'dont_redirect':True})

	def send_information(self, response):
		print response.status
		if 'location' in response.headers:
			url = response.urljoin(response.headers['Location'])
			yield Request(url, self.parse_result,
						headers={'X-Requested-With':'XMLHttpRequest'}
						)

	def parse_result(self, response):
		print response.status
		data = loads(response.body)
		bFinalized = data['finalizado']
		if bFinalized == False:
			yield Request(response.url, self.parse_result,
						headers={'X-Requested-With':'XMLHttpRequest'},
						dont_filter=True
						)

		else: # Received Final packet
			cotizaciones = data['cotizaciones']
			sel = Selector(text=cotizaciones)

			ins_types = sel.xpath('//*[@class="row"]/div')
			for ins_t in ins_types:
				ins_t_name = ins_t.xpath('./a/div/text()').extract_first()
				companies = ins_t.xpath('./div')
				for company in companies:
					company_name = self.get_companyname(company.xpath('./img/@src').extract_first())
					price = company.xpath('./span/text()').extract_first().replace('$','').replace('.','').replace(',','.')
					print ins_t_name, company_name, price					

	def get_companyname(self, img):
		if "provincia" in img:
			return "Provincia"

		elif "rio_uruguay_c" in img:
			return "Rio Uruguay"

		elif "allianz" in img:
			return "Allianz"

		elif "holando" in img:
			return "La Holando"

		elif "mapfre" in img:
			return "Mapfre"

		elif "sura" in img:
			return "Sura"

		elif "zurich" in img:
			return "Zurich"

		elif "nacion" in img:
			return "Nacion"

		return "Unknow"
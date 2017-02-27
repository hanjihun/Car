# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest, Selector

from datetime import date
from collections import OrderedDict

from json import loads
from random import randint

import json, re, collections
import datetime, time
import logging

# Remove below package when publishing
from scrapy.utils.response import open_in_browser

class CompresegurosComSpider(scrapy.Spider):

	name = "compreseguros_com_spider"
	start_urls = ['https://www.compreseguros.com/']

	handle_httpstatus_list = [302]
	#custom_settings = {'DOWNLOAD_DELAY' : 10}

	headers = {}
	headers['Upgrade-Insecure-Requests'] = "1"
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	headers['Content-Type'] = 'application/x-www-form-urlencoded'
	headers['Cache-Control:'] = "max-age=0"
	headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
	headers['Accept-Encoding'] = "gzip, deflate, br"

	def __init__(self, categories=None, *args, **kwargs):
		super(CompresegurosComSpider, self).__init__(*args, **kwargs)
		#pass
		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		self.sub_urls = loads(self.categories).keys()


	# CHEVROLET---AGILE*1.4*LS*L/14---2016---40---12---163---120462---LA*PAMPA---LOS*OLIVOS---8203
	def parse(self, response):
		logging.info("I am called from parse method")
		for index, param in enumerate(self.sub_urls):
			print param
			
			url = "https://www.compreseguros.com/seguros-de-autos"

			formdata = {}
			formdata['cotizacion[infoauto_marca]'] = param.split('---')[4]#'12'
			formdata['cotizacion[anio]'] = param.split('---')[2]#'2016'
			formdata['cotizacion[infoauto_grupo]'] = param.split('---')[5]#'163'
			formdata['cotizacion[infoauto_codigo]'] = param.split('---')[6]#'120462'
			formdata['cotizacion[tiene_gnc]'] = '0'
			formdata['cotizacion[sexo]'] = 'm'
			formdata['cotizacion[estado_civil]'] = 'casado'
			formdata['cotizacion[email]'] = 'adegs@yahoo.com'
			formdata['cotizacion[codigo_postal]'] = param.split('---')[-1]#'1428'
			formdata['cotizacion[tel_area]'] = '011'
			formdata['cotizacion[tel_numero]'] = "55554444"#str(randint(50000000, 90000000))
			formdata['cotizacion[edad]'] = param.split('---')[3]#'40'
			formdata['cotizacion[_csrf_token]'] = response.xpath('//input[@id="cotizacion__csrf_token"]/@value').extract_first()

			# # formdata['cotizacion[infoauto_marca]'] = '12'
			# # formdata['cotizacion[anio]'] = '2016'
			# # formdata['cotizacion[infoauto_grupo]'] = '163'
			# # formdata['cotizacion[infoauto_codigo]'] = '120462'
			# # formdata['cotizacion[tiene_gnc]'] = '0'
			# # formdata['cotizacion[sexo]'] = 'm'
			# # formdata['cotizacion[estado_civil]'] = 'casado'
			# # formdata['cotizacion[email]'] = 'baduk@gmail.com'
			# # formdata['cotizacion[codigo_postal]'] = '1428'
			# # formdata['cotizacion[tel_area]'] = '011'
			# # formdata['cotizacion[tel_numero]'] = "55554444"#str(randint(50000000, 90000000))
			# # formdata['cotizacion[edad]'] = '39'
			# # formdata['cotizacion[_csrf_token]'] = response.xpath('//input[@id="cotizacion__csrf_token"]/@value').extract_first()
			stime = int(time.time())
			yield FormRequest(url, self.send_information, method="POST", formdata=formdata,\
						 meta={'dont_redirect':True, 'param':param, 'idx':index, 'stime':stime, 'frmdata':formdata}, headers=self.headers)
			

	def parse1(self, response):
		url = "https://www.compreseguros.com/seguros-de-autos"
		formdata = response.meta['frmdata']		
		formdata['cotizacion[_csrf_token]'] = response.xpath('//input[@id="cotizacion__csrf_token"]/@value').extract_first()

		stime = response.meta['stime']
		yield FormRequest(url, self.send_information, method="POST", formdata=formdata,\
					 meta={'dont_redirect':True, 'param':response.meta['param'], 'idx':response.meta['idx'], 'stime':stime, 'frmdata':formdata},\
					 headers=self.headers, dont_filter=True)


	def send_information(self, response):
		print response.status

		#print response.headers
		if 'location' in response.headers:
			url = response.urljoin(response.headers['Location'])
			index = response.meta['idx']
			stime = response.meta['stime']
			yield Request(url, self.parse_result,
						headers={'X-Requested-With':'XMLHttpRequest'},
						meta={'param':response.meta['param'], 'idx':index, 'stime':stime, 'times':1, 'frmdata':response.meta['frmdata'],
						},dont_filter = True
						)
		else:
			print " ########################################################## "
			print " ########################################################## "
			print " ########################################################## "
			print " ########################################################## "
			print response.meta['idx'], "Error "
			print " ########################################################## "
			print " ########################################################## "
			print " ########################################################## "
			print " ########################################################## "

	def parse_result(self, response):
		#print response.status

		# Log Section
		stime = response.meta['stime']
		index = response.meta['idx']
		times = response.meta['times']
		ctime = int(time.time())
		print "#", index,"th combination elasped ", ctime-stime,"s by ", times,"trying."
		# Log Section

		param = response.meta['param']
		data = loads(response.body)
		bFinalized = data['finalizado']
		if bFinalized == False:
			if times > 20:
				yield Request(self.start_urls[0], self.parse1, dont_filter=True,
							meta={'frmdata':response.meta['frmdata'], 'idx':index, 'stime':stime, 'param':param})
			else:
				yield Request(response.url, self.parse_result,
						headers={'X-Requested-With':'XMLHttpRequest'},
						dont_filter=True,
						meta={'param':response.meta['param'], 
								'stime':stime, 'idx':index, 'times':times+1, 'frmdata':response.meta['frmdata']}
						)

		else: # Received Final packet
			print "$$$",index,"th combination completed. for {} seconds".format(ctime-stime), times,"times.","$$$"
			cotizaciones = data['cotizaciones']
			sel = Selector(text=cotizaciones)

			ins_types = sel.xpath('//*[@class="row"]/div')
			for ins_t in ins_types:
				ins_t_name = ins_t.xpath('./a/div/text()').extract_first()
				companies = ins_t.xpath('./div')
				for company in companies:
					# CHEVROLET---AGILE*1.4*LS*L/14---2016---40---12---163---120462---LA*PAMPA---LOS*OLIVOS---8203
					company_name = self.get_companyname(company.xpath('./img/@src').extract_first())
					if company_name == "Unknown":
						company_name = company.xpath('./img/@src').extract_first()
					price = company.xpath('./span/text()').extract_first().replace('$','').replace('.','').replace(',','.')
					
					item = OrderedDict()
					item['Vendedor'] = 429
					item['Model'] = param.split('---')[1].replace('*',' ')
					item['Brand'] = param.split('---')[0].replace('*',' ')
					item['Year'] = param.split('---')[2]
					item['Location'] = param.split('---')[-3].replace('*',' ') + " " + param.split('---')[-2].replace('*',' ')
					item['Age'] = param.split('---')[3]
					item['Date'] = date.today()
					item['Company'] = company_name
					item['Insurance Type'] = ins_t_name
					item['Price'] = price
					item['Currency'] = "ARS"

					yield item

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

		elif "rsa_c" in img:
			return "Sura"

		elif "zurich" in img:
			return "Zurich"

		elif "nacion" in img:
			return "Nacion"

		return "Unknown"
	
	def convert(self, data):
		if isinstance(data, basestring):
			return str(data)
		elif isinstance(data, collections.Mapping):
			return dict(map(self.convert, data.iteritems()))
		elif isinstance(data, collections.Iterable):
			return type(data)(map(self.convert, data))
		else:
			return data
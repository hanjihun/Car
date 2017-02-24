# -*- coding: utf-8 -*-
import scrapy

from scrapy import Request, FormRequest
from urlparse import urlparse
from collections import OrderedDict
from datetime import date

import time, json, re, csv


class CategoriesOfCompresegurosCom(scrapy.Spider):

	name = "categories_of_compreseguros_com"

	start_urls = ['https://www.compreseguros.com/']

	def parse(self, response):
		brand_url = "https://gestion.compreseguros.com/comun/infoauto/api/v1/marcas"

		yield Request(brand_url, self.get_brands)

	def get_brands(self, response):
		brands = json.loads(response.body)['result']
		
		for brand in brands:
			print brand['id'], brand['descripcion']	
			# if brand['id'] != "12":
			# 	continue
			year_url = "https://gestion.compreseguros.com/comun/infoauto/api/v1/precios?filter%5Bmarca%5D={}&group%5B%5D=anio".format(brand['id'])
			yield Request(year_url, self.get_years, meta={'info':brand})
			

	def get_years(self, response):
		years = json.loads(response.body)['result']
		info = response.meta['info']
		for year in years:
			# if year['anio'] != "2016":
			# 	continue
			info1 = year
			info1.update(info)
			print year['modelo_id'],year['anio'],year['monto']
			model_url = "https://gestion.compreseguros.com/comun/infoauto/api/v1/grupos?filter%5Bmarca%5D={}&filter%5Banio%5D={}".format(info['id'],year['anio'])
			yield Request(model_url, self.get_models, meta={'info':info1})
			

	def get_models(self, response):
		models = json.loads(response.body)['result']
		info = response.meta['info']
		print info
		for model in models:
			print model['id'],model['marca_id'],model['descripcion']
			version_url = "https://gestion.compreseguros.com/comun/infoauto/api/v1/modelos?filter%5Bmarca%5D={}&filter%5Banio%5D={}&filter%5Bgrupo%5D={}".\
				format(info['id'], info['anio'], model['id'])
			info1 = {'model_desc':model['descripcion'], 'model_id':model['id']}
			info1.update(info)
			yield Request(version_url, self.get_versions, meta={'info':info1})
			

	def get_versions(self, response):
		versions = json.loads(response.body)['result']
		info = response.meta['info']
		print info
		for version in versions:
			print version['id'], version['descripcion'], version['grupo_id']
			yield OrderedDict({'brand':info['descripcion'], 'version':version['descripcion'], 'year':info['anio'], 'age':'40','brand_id':version['marca_id'], \
								'model_id':version['grupo_id'], 'version_id':version['id']})


	
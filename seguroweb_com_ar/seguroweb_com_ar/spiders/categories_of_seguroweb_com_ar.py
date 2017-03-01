import scrapy

from scrapy import Request, FormRequest
from urlparse import urlparse
from collections import OrderedDict
from datetime import date

import time, json, re, csv


class CategoriesOfSegurowebComAr(scrapy.Spider):

	name = "categories_of_seguroweb_com_ar"

	start_urls = ['http://seguroweb.com.ar/autos/']

	brand_model_list_file_name = "brand_model_list.csv"
	location_list_file_name = "location_list.csv"

	def parse(self, response):

		brand_model_list = []
		location_list = []

		with open(self.brand_model_list_file_name, 'rb') as brand_model_list_file:
			reader = csv.reader(brand_model_list_file)
			for index, row in enumerate(reader):
				if index == 0:
					continue
				brand_model_list.append({'brand_name':row[0], 'brand_id':row[1], 'version_name':row[2], 'model_id':row[3], 'version_id':row[4], 'year':row[5], 'age':row[6]})

		with open(self.location_list_file_name, 'rb') as location_list_file:
			reader = csv.reader(location_list_file)

			for index, row in enumerate(reader):
				if index == 0:
					continue
				location_list.append({'prov_name':row[0], 'city_name':row[1], 'prov_id':row[2], 'city_id':row[3]})

		links = []
		# CHEVROLET---AGILE*1.4*LS*L/14---2013---40---12---56---120360---LA*PAMPA---LOS*OLIVOS---2---18385
		for location in location_list:
			for brand_model in brand_model_list:
				link = brand_model['brand_name'].replace(' ','*') + "---" + brand_model['brand_id'].replace(' ','*') + "---" + brand_model['year'] + "---" + brand_model['age'] + "---" + brand_model['brand_id'] +	"---" + brand_model['model_id'] + "---" + brand_model['version_id']
				link = link + "---" + location['prov_name'].replace(' ','*') + "---" + location['city_name'].replace(' ','*') + "---" + location['prov_id'] + "---" + location['city_id']
				
				links.append(link)

		yield {'links':links}

	### To list the zip code and the location name. Output the result .
	### Do not delete below code ###
	def parse_for_models(self, response):
		brands = response.xpath('//*[@name="marca"]/optgroup/option')
		for brand in brands:
			id = brand.xpath('@value').extract_first()
			name = brand.xpath('text()').extract_first()
			info = {'brand_id':id, 'brand_name':name}
			url = "http://seguroweb.com.ar/autos/version.php?id={}&id2=undefined".format(id)
			yield Request(url, self.get_models, meta={'info':info})
			
	def get_models(self, response):
		models = response.xpath('//*[@name="version"]/option[position()>1]')
		info = response.meta['info']
		for model in models:
			id = model.xpath('@value').extract_first()
			name = model.xpath('text()').extract_first()
			
			info1 = {'model_id':id, 'model_name':name}
			info1.update(info)
			url = "http://seguroweb.com.ar/autos/modelo.php?id={}&id2={}".format(id, info['brand_id'])
			yield Request(url, self.get_versions, meta={'info':info1})
			
	def get_versions(self, response):
		versions = response.xpath('//*[@name="modelo"]/option[position()>1]')
		info = response.meta['info']
		for version in versions:
			id = version.xpath('@value').extract_first()
			name = version.xpath('text()').extract_first()
			info1 = {'version_id':id, 'version_name':name}
			info1.update(info)
			url = "http://seguroweb.com.ar/autos/anio.php?id={}&id2=undefined".format(id)
			yield Request(url, self.get_years, meta={'info':info1})


	def get_years(self, response):
		years = response.xpath('//*[@name="anio"]/option[position()>1]')
		info = response.meta['info']
		print info
		for year in years:
			id = year.xpath('@value').extract_first()
			name = year.xpath('text()').extract_first()

			item = OrderedDict()
			item['brand_name'] = info['brand_name']
			item['brand_id'] = info['brand_id']
			item['version_name'] = info['version_name']
			item['model_id'] = info['model_id']
			item['version_id'] = info['version_id']
			item['year'] = id
			item['age'] = "40"

			yield item


	def parse_for_location(self, response):
		print "##"
		provinces = response.xpath('//*[@name="provincia"]/option[position()>1]')
		for province in provinces:
			id = province.xpath('@value').extract_first()
			name = province.xpath('text()').extract_first()
						
			url = "http://seguroweb.com.ar/autos/localidad.php?id={}&id2=undefined".format(id)
			yield Request(url, self.get_cities, meta={'province_id':id, 'province_name':name})
			

	def get_cities(self, response):
		cities = response.xpath('//*[@name="localidad"]/option[position()>1]')
		for city in cities:
			id = city.xpath('./@value').extract_first()
			name = city.xpath('./text()').extract_first()
			
			yield {'prov_name':response.meta['province_name'], 'city_name':name, 'prov_id':response.meta['province_id'], 'city_id':id}
		
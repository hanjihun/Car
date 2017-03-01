import scrapy

from scrapy import Request, FormRequest
from urlparse import urlparse
from collections import OrderedDict
from datetime import date

import time, json, re, csv


class CategoriesOfSeguruComAr(scrapy.Spider):

	name = "categories_of_seguru_com_ar"

	start_urls = ['http://www.seguru.com.ar/']

	brand_model_list_file_name = "brand_model_list.csv"
	location_list_file_name = "location_list.csv"

	headers = {}
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	headers['X-Requested-With']='XMLHttpRequest'

	def parse(self, response):

		brand_model_list = []
		location_list = []

		with open(self.brand_model_list_file_name, 'rb') as brand_model_list_file:
			reader = csv.reader(brand_model_list_file)
			for index, row in enumerate(reader):
				if index == 0:
					continue
				brand_model_list.append({'brand_name':row[0], 'brand_id':row[1], 'model_name':row[2], 'model_id':row[3], 'year_id':row[4], 'year_name':row[5], 'age':row[6]})

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
				link = brand_model['brand_name'].replace(' ','*') + "---" + brand_model['model_name'].replace(' ','*') + "---" + brand_model['brand_id'] + "---" + brand_model['model_id'] + "---" + brand_model['year_id'] + "---" + brand_model['year_name'] + "---" + brand_model['age']
				link = link + "---" + location['prov_name'].replace(' ','*') + "---" + location['city_name'].replace(' ','*') + "---" + location['prov_id'] + "---" + location['city_id']
				
				links.append(link)

		yield {'links':links}

	### To list the zip code and the location name. Output the result .
	### Do not delete below code ###
	def parse_for_brand(self, response):
		brands = response.xpath('//*[@id="brand"]/option[position()>1]')
		for brand in brands:
			id = brand.xpath('@value').extract_first()
			name = brand.xpath('text()').extract_first()
			#id = "94"
			info = {'brand_id':id, 'brand_name':name}			
			url = "http://www.seguru.com.ar/years/get_list_by_brand/{}.json".format(id)
			
			yield Request(url, self.get_years, meta={'info':info}, headers=self.headers)
			

	def get_years(self, response):
		data = json.loads(response.body)
		info = response.meta['info']
		if data:
			for id in data.keys():
				name = data[id]
				info1 = {'year_id':id, 'year_name':name}
				info1.update(info)
				#id = "20"
				url = "http://www.seguru.com.ar/car_models/get_list_by_brand_year/{}/{}.json".format(info['brand_id'], id)
				yield Request(url, self.get_models, meta={'info':info1}, headers=self.headers)
			

	def get_models(self, response):
		data = json.loads(response.body)
		info = response.meta['info']
		if data:
			for id in data.keys():
				name = data[id]
				info1 = {'model_id':id, 'model_name':name}
				
				item = OrderedDict()
				item['brand_name'] = info['brand_name']
				item['brand_id'] = info['brand_id']
				item['model_name'] = name
				item['model_id'] = id
				item['year_id'] = info['year_id']
				item['year_name'] = info['year_name']
				item['age'] = "40"
				yield item

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


	def get_years2(self, response):
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
		provinces = response.xpath('//*[@id="province"]/option[position()>1]')
		for prov in provinces:
			id = prov.xpath('./@value').extract_first()
			name = prov.xpath('./text()').extract_first()
			print id, name
			url = "http://www.seguru.com.ar/localities/get_list/{}.json".format(id)
			yield Request(url, self.get_cities, meta={'province_name':name, 'province_id':id}, headers=self.headers)

	def get_cities(self, response):
		data = json.loads(response.body)
		for id in data.keys():
			
			yield {'prov_name':response.meta['province_name'], 'city_name':data[id], 'prov_id':response.meta['province_id'], 'city_id':id}
		
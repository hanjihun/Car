import scrapy

from scrapy import Request, FormRequest
from urlparse import urlparse
from collections import OrderedDict
from datetime import date

import time, json, re, csv


class CategoriesOfWww123seguroCom(scrapy.Spider):

	name = "categories_of_www_123seguro_com"

	start_urls = ['https://www.123seguro.com/']

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
				brand_model_list.append({'model_id':row[0], 'brand':row[1], 'version':row[2], 'year':row[3], 'model':row[4], 'age':row[5]})

		with open(self.location_list_file_name, 'rb') as location_list_file:
			reader = csv.reader(location_list_file)

			for index, row in enumerate(reader):
				if index == 0:
					continue
				location_list.append({'prov_name':row[0], 'city_name':row[1], 'zipcode':row[2], 'city_id':row[3]})

		links = []
		for location in location_list:
			for brand_model in brand_model_list:
				link = brand_model['model_id'] + "---" + brand_model['brand'].replace(' ','*') + "---" + brand_model['model'].replace(' ','*')+ "---" + brand_model['year'] + "---" + brand_model['age']
				link = link + "---" + location['prov_name'].replace(' ','*') + "---" + location['city_name'].replace(' ','*') + "---" + location['zipcode'] + "---" + location['city_id']
				
				links.append(link)

		yield {'links':links}				
	### To list the zip code and the location name. Output the result in json format.
	### Do not delete below code ###

	# def parse(self, response):
	# 	province_data = json.loads(response.xpath('//*[@id="data-prov"]/text()').extract_first())
	# 	for index, prov in enumerate(province_data):
	# 		if index == 0:
	# 			continue
	# 		print prov['id'], ' ', prov['nombre']
	# 		url = "https://www.123seguro.com/localidades?provincia_id={}".format(prov['id'])
	# 		info = {'prov_id':prov['id'], 'prov_name':prov['nombre']}
	# 		yield Request(url, callback=self.parse_province, meta={'info':info})
			
	# def get_url_string(self, str):
	# 	return str.replace(" ", "*")

	# def parse_province(self, response):
		
	# 	info = response.meta['info']

	# 	cities = json.loads(response.body)

	# 	links = []
	# 	for city in cities:
	# 		#print city['nombre'], city['id'], city['provincia_id'], city['cp']
	# 		info['city_id'] = city['id']
	# 		info['city_name'] = city['nombre']
	# 		info['zipcode'] = city['cp']

	# 		links.append(self.get_url_string(info['prov_name']) + "---" + self.get_url_string(info['city_name']) + "---" + city['cp'] + "---" + city['id'])
	# 		#yield info

	# 	if links:
	# 		yield {"links":links}
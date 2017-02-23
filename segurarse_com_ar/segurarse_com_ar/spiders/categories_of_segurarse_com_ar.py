# -*- coding: utf-8 -*-

from scrapy import Spider, Request, FormRequest
from collections import OrderedDict
import json,csv

class CategoriesOfSegurarseComAr(Spider):

	name = "categories_of_segurarse_com_ar"

	start_urls = ['https://segurarse.com.ar/cotizador-de-seguros-auto',]

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
				brand_model_list.append({'brand':row[0], 'version':row[1], 'year':row[2], 'model':row[3], 'age':row[4]})

		with open(self.location_list_file_name, 'rb') as location_list_file:
			reader = csv.reader(location_list_file)

			for index, row in enumerate(reader):
				if index == 0:
					continue
				location_list.append({'prov_name':row[0], 'city_name':row[1], 'zipcode':row[2]})

		links = []
		for location in location_list:
			for brand_model in brand_model_list:
				link = brand_model['brand'].replace(' ','*') + "---" + brand_model['version'].replace(' ','*')+ "---" + brand_model['year'] + "---" + brand_model['age']
				link = link + "---" + location['prov_name'].replace(' ','*') + "---" + location['city_name'].replace(' ','*') + "---" + location['zipcode']
				
				links.append(link)

		yield {'links':links}


	### To list the zip code and the location name.
	### Do not delete below code ###
	# def parse(self, response):

	# 	brands = response.xpath('//*[@id="Marca"]/option/@value').extract()
		
	# 	#brands = [x if x and not "--" in x else "XXX" for x in brands]
	# 	brands = [x for x in brands if x and not "--" in x]

	# 	for brand in brands:
	# 		print brand

	# 		url = "https://segurarse.com.ar/Auto/AsyncModelos"			
	# 		yield FormRequest(url, self.get_models, formdata={"Marca":brand}, method="POST")
			
	
	# def get_models(self, response):

	# 	models = json.loads(response.body)
	# 	for model in models:
	# 		print model['Text'],model['Value']
	# 		url = "https://segurarse.com.ar/Auto/AsyncAnios"
	# 		yield FormRequest(url, self.get_years, formdata={"Modelo":model['Value']}, method="POST", meta={'model':model})
			

	# def get_years(self, response):

	# 	years = json.loads(response.body)
	# 	for year in years:
	# 		print year['Value']
	# 		url = "https://segurarse.com.ar/Auto/AsyncVersiones"
	# 		yield FormRequest(url, self.get_versions, formdata={"Anio":year['Value']}, method="POST", meta={'year':year})

	# def get_versions(self, response):

	# 	info = response.meta['year']['Value']
	# 	brand, model, year = info.split(';')

	# 	versions = json.loads(response.body)
	# 	for version in versions:
	# 		#print brand, model, year, version['Value']
	# 		item = OrderedDict()
	# 		item['brand'] = brand
	# 		item['version'] = version['Value']
	# 		item['model'] = model
	# 		item['year'] = year
	# 		item['age'] = "40"
	# 		yield item

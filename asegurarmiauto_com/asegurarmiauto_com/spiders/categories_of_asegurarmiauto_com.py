import scrapy

from scrapy import Request
from collections import OrderedDict
from urlparse import urlparse
import time, json, csv

class CategoriesOfAsegurarmiautoCom(scrapy.Spider):

	name = "categories_of_asegurarmiauto_com"
	start_urls = ['http://www.asegurarmiauto.com/']

	headers = {}
	headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
	headers['X-Wokan-Webpack-SID'] = "asegurarmiauto"

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
				brand_model_list.append({'brand_name':row[0], 'version_name':row[1], 'year':row[2], 'age':row[3], 'version_id':row[4]})

		with open(self.location_list_file_name, 'rb') as location_list_file:
			reader = csv.reader(location_list_file)

			for index, row in enumerate(reader):
				if index == 0:
					continue
				location_list.append({'prov_name':row[0], 'city_name':row[1], 'zipcode':row[2]})

		links = []
		for location in location_list:
			for brand_model in brand_model_list:
				link = brand_model['brand_name'] + "---" + brand_model['version_name'].replace(' ','*') + "---" + brand_model['year']+ "---" + brand_model['version_id'] + "---" + brand_model['age']
				link = link + "---" + location['prov_name'].replace(' ','*') + "---" + location['city_name'].replace(' ','*') + "---" + location['zipcode']

				links.append(link)

		yield {'links':links}


	def parse1(self, response):	

		get_marca_url = "http://webpack.wokan.com.ar/api/v1/infoauto/marcas"
		yield Request(get_marca_url, callback=self.parse_marca, headers=self.headers)

	def parse_marca(self, response):
		
		marcas = json.loads(response.body)
		
		marca_list = marcas['result']
		for m in marca_list:
			print m['descripcion'], " ",m['id']
			get_date_url = "http://webpack.wokan.com.ar/api/v1/infoauto/precios?filter%5Bmarca%5D={}&group%5B%5D=anio".format(m['id'])
			yield Request(get_date_url, callback=self.parse_date, headers=self.headers, meta={'info':{'brand_name':m['descripcion'], 'brand_id':m['id']}})
			

	def parse_date(self, response):
		
		years = json.loads(response.body)
		years_list = years['result']
		info = response.meta['info']
		for y in years_list:
			print y['anio']
			get_model_url = "http://webpack.wokan.com.ar/api/v1/infoauto/grupos?filter%5Bmarca%5D={}&filter%5Banio%5D={}".format(info['brand_id'], y['anio'])
			info1 = {'year':y['anio']}
			info1.update(info)
			yield Request(get_model_url, callback=self.parse_model, headers=self.headers, meta={'info':info1})
			

	def parse_model(self, response):

		models = json.loads(response.body)['result']
		info = response.meta['info']
		for m in models:
			print m
			info1 = {'model_name':m['descripcion'], 'model_id':m['id']}
			info1.update(info)
			get_version_url = "http://webpack.wokan.com.ar/api/v1/infoauto/modelos?filter%5Bmarca%5D={}&filter%5Banio%5D={}&filter%5Bgrupo%5D={}".format(info['brand_id'],info['year'], m['id'])
			yield Request(get_version_url, callback=self.parse_version, headers=self.headers, meta={'info':info1})
			

	def parse_version(self, response):
		versions =json.loads(response.body)['result']
		info = response.meta['info']
		links = []
		for v in versions:
			#print v['descripcion'], v['id']
			item = OrderedDict()
			item = {'brand_name':info['brand_name'], 'version':v['descripcion'], 'year':info['year'], 'version_id':v['id'], 'age':'40'}
			yield item
		# 	result = response.meta['anio']+"---"+v['id']
		# 	links.append(result)

		# yield {'links':links}

import scrapy

from scrapy import Request, FormRequest
from urlparse import urlparse
import time, json, csv
from scrapy.conf import settings
from collections import OrderedDict

class CategoriesOfAseguraronlineCom(scrapy.Spider):

	name = "categories_of_aseguraronline_com"
	start_urls = ['http://www.aseguraronline.com/seguros-para-autos']

 	settings.overrides['CONCURRENT_REQUESTS_PER_DOMAIN'] = 16
 	settings.overrides['DOWNLOAD_DELAY'] = 0.1
	use_selenium = False
	# headers = {}
	# headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
	# headers['X-Wokan-Webpack-SID'] = "asegurarmiauto"

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
				brand_model_list.append({'brand_name':row[0], 'model_name':row[1], 'brand_id':row[2], 'model_id':row[3], 'year':row[4], 'age':row[5]})

		with open(self.location_list_file_name, 'rb') as location_list_file:
			reader = csv.reader(location_list_file)

			for index, row in enumerate(reader):
				if index == 0:
					continue
				location_list.append({'prov_name':row[0], 'city_name':row[1], 'zipcode':row[2]})

		links = []
		for location in location_list:
			for brand_model in brand_model_list:
				link = brand_model['brand_name'] + "---" + brand_model['brand_id'] + "---" + brand_model['model_name'].replace(' ','*')+ "---" + brand_model['model_id'] + "---" + brand_model['year']+ "---" + brand_model['age']
				link = link + "---" + location['prov_name'].replace(' ','*') + "---" + location['city_name'].replace(' ','*') + "---" + location['zipcode']
				
				links.append(link)

		yield {'links':links}

	### To list the zip code and the location name. Output the result in json format.
	### Do not delete below code ###
	def parse1(self, response):		
		get_marca_url = "http://aolprod-elb-872623335.sa-east-1.elb.amazonaws.com/api/v1/car/brands"
		yield Request(get_marca_url, callback=self.parse_marca)

	def parse_marca(self, response):
		marcas = json.loads(response.body)
		
		for m in marcas:
			print m['label'], " ",m['id']
			get_model_url = "http://aolprod-elb-872623335.sa-east-1.elb.amazonaws.com/api/v1/modelcar/{}".format(m['id'])
			marca = {'id':m['id'], 'label':m['label']}
			yield Request(get_model_url, callback=self.parse_model, meta={'marca':marca})
			


	def parse_model(self, response):

		models = json.loads(response.body)['data']
		for m in models:
			#print m['idmodelo'], " ", m['nombre']

			get_date_url = "http://aolprod-elb-872623335.sa-east-1.elb.amazonaws.com/api/v1/car/brand/{}".format(m['idmodelo'])
			model = {'id':m['idmodelo'], 'label':m['nombre']}
			yield Request(get_date_url, callback=self.parse_date, meta={'marca':response.meta['marca'], 'model':model})
			

	def parse_date(self, response):
		#print response.body
		years = json.loads(response.body)
		marca = response.meta['marca']
		model = response.meta['model']
		links = []
		for y in years:
			#print y['id'], " ", y['label']
			item = OrderedDict()
			item['brand_name'] = marca['label']			
			item['model_name'] = model['label']
			item['brand_id'] = marca['id']
			item['model_id'] = model['id']
			item['year'] = y['label']

			yield item
			#link = marca['id'] + "---" + marca['label'] + "---" + model['id'] + "---" + model['label'].replace(' ','*') + "---" + y['id'] + "---" + y['label']

		# 	links.append(link)

		# if links:
		# 	yield {'links':links}


import scrapy

from scrapy import Request, FormRequest
from urlparse import urlparse
from collections import OrderedDict
from datetime import date

import time, json, re, csv


class CategoriesOfSeguros911ComAr(scrapy.Spider):

	name = "categories_of_seguros911_com_ar"

	start_urls = ['https://www.seguros911.com.ar/']

	brand_model_list_file_name = "brand_model_list.csv"
	location_list_file_name = "location_list.csv"

	headers = {}
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	headers['X-Requested-With']='XMLHttpRequest'
	#"TOYOTA---COROLLA*1.8*XLI**********L/08---2003---40---450159---Buenos*Aires,*Barrio*Parque*Leloir(1713)---1---1713---16447"
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
				location_list.append({'prov_name':row[0], 'prov_id':row[1], 'zip':row[2], 'loc_id':row[3]})

		links = []
		# CHEVROLET---AGILE*1.4*LS*L/14---2013---40---12---56---120360---LA*PAMPA---LOS*OLIVOS---2---18385
		for location in location_list:
			for brand_model in brand_model_list:
				link = brand_model['brand_name'].replace(' ','*') + "---" + brand_model['version_name'].replace(' ','*') + "---" + brand_model['year'] + "---" + brand_model['age'] + "---" + brand_model['version_id']
				link = link + "---" + location['prov_name'].replace(' ','*') + "---" + location['prov_id'].replace(' ','*') + "---" + location['zip'] + "---" + location['loc_id']
				
				links.append(link)

		yield {'links':links}

	### To list the zip code and the location name. Output the result .
	### Do not delete below code ###
	def parse_for_brands(self, response):
		brandString = re.findall('var marcas_ids = (.*);', response.body)
		data =json.loads( brandString[0])
		url = "https://www.seguros911.com.ar/process/ajax_process.php"
		for brand in data:
			id = brand['value']
			name = brand['label']

			# id = "45"
			# name = "TOYOTA"
			
			info = {'brand_id':id, 'brand_name':name}
			formdata = {'tipo':"getModelos", 'marca[id]':id, 'marca[desc]':name}

			yield FormRequest(url, self.get_models, method="POST", formdata=formdata, meta={'info':info})

	def get_models(self, response):
		data = json.loads(response.body)['modelos']
		info = response.meta['info']
		url = "https://www.seguros911.com.ar/process/ajax_process.php"
		for model in data:
			id = model['value']
			name = model['label']
			# id = "8"
			# name = "COROLLA"
			info1 = {'model_id':id, 'model_name':name}
			info1.update(info)
			formdata = {'tipo':'getAniosYVersiones', 'marca[id]':info['brand_id'], 'marca[desc]':info['brand_name'], 'modelo[id]:':id, 'modelo[desc]':name}
			yield FormRequest(url, self.get_yearsversions, method="POST", formdata=formdata, meta={'info':info1})
			
	def get_yearsversions(self, response):
		info = response.meta['info']
		print info		
		versions = json.loads(response.body)['versiones']
		years_versions = json.loads(response.body)['anios_versiones']
		for version in versions:
			print version['id_version'], version['descripcion'], version['infoautocod']
			for year in years_versions:
				if year['id_version'] == version['id_version']:
					#print year['anio']
					item = {}
					item['brand_name'] = info['brand_name']
					item['version_name'] = version['descripcion']
					item['version_id'] = version['infoautocod']
					item['year'] = year['anio']
					item['age'] = "40"
					yield item

	def parse_for_loc(self, response):
		print "##"
		with open('zip.txt', 'rb') as f:
			content = f.readlines()
		content = [x.strip() for x in content]
		for index, code in enumerate(content):
			print code
			url = "https://www.seguros911.com.ar/process/ajax_process.php"
			formdata = {'tipo':'getProvLoc', 'locCodpostStr':code}
			yield FormRequest(url, self.parse_zip, method="POST", formdata=formdata)
			
	def parse_zip(self, response):
		print response.body
		if json.loads(response.body)['error'] == False:
			data = json.loads(response.body)['prov_loc']
			for loc in data:
				
				yield {'prov_name':loc['prov_loc'], 'prov_id':loc['prov_id'], 'loc_id':loc['loc_id'], 'cp':loc['cp']}
		
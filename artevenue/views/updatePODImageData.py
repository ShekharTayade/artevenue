from artevenue.models import Stock_image_category, Product_type, Tax
from artevenue.models import Stock_image, Stock_image_stock_image_category
from artevenue.models import Ecom_site, Publisher_price, Publisher
from artevenue.models import Stock_image_error, Stock_image_category_error, Publisher_error, Stock_image_stock_image_category_error, Image_url_error

from datetime import datetime
from django.conf import settings
from decimal import Decimal
import csv
import urllib
import datetime
import codecs
from pathlib import Path

from PIL import Image, ImageFilter
import requests
from io import BytesIO

from urllib.error import URLError, HTTPError

ecom = Ecom_site.objects.get(store_id=settings.STORE_ID )
today = datetime.date.today()

def importPODImageData(): 

	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	file = urllib.request.urlopen(url)
	if file.code != 200:
		print ("File not found on POD!")
		return
		
	cr = csv.reader(codecs.iterdecode(file, 'utf-8'))	
	
	#cr = csv.reader(csvfile, delimiter=',')

	cnt = 0
	'''Get Product type (IMAGE) '''
	prod_type = Product_type.objects.filter(product_type_id__iexact = "STOCK-IMAGE", store = ecom).first()
	'''Get Tax code for IMAGE '''
	prod_tax = Tax.objects.filter(name__iexact = "STOCK-IMAGE", store = ecom).first()
	tax_rate = prod_tax.tax_rate

	import wget
	img_dir = "/home/artevenue/website/estore/static/image_data/POD/images/"
	
	for row in cr:
		print(cnt)
		# Skip the first row (header)
		if cnt == 0:
			cnt = cnt + 1
			continue

		if row[0]:
			prod = Stock_image.objects.filter(product_id = int(row[0])).first()
			if not prod:
				## Low Resolution Image
				lowres_url = row[11]
				print("NEW:- " + lowres_url)
				try:
					fl =  urllib.request.urlopen(lowres_url)
				except HTTPError as e:
					print('Error code: ', e.code)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + lowres_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
				except URLError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + lowres_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
				except ValueError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + lowres_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
					
				if fl.code == 200:
					pos = lowres_url.rfind('/')
					loc = 0
					if pos > 0:
						loc = pos+1
					lowres_img = lowres_url[loc:]
					file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img)
					# If file does not exists then copy the file
					if not file.is_file():	
						print(lowres_url)
						wget.download(lowres_url, out=img_dir)
					
				thumbnail_url = row[12]
				try :
					ft =  urllib.request.urlopen(thumbnail_url)
				except HTTPError as e:
					print('Error code: ', e.code)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + thumbnail_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
				except URLError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + thumbnail_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
				except ValueError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + thumbnail_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
					
				if ft.code == 200:
					pos = thumbnail_url.rfind('/')
					loc = 0
					if pos > 0:
						loc = pos+1
					thumbnail_img = thumbnail_url[loc:]
					file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
					# If file does not exists then copy the file
					if not file.is_file():	
						print(thumbnail_url)
						wget.download(thumbnail_url, out=img_dir)
							
			
			'''					'''
			''' Publisher 		'''
			'''					'''
			try:
				publisher = Publisher.objects.filter(publisher_id = row[1]).first()
				if not publisher:
					pub = 	Publisher( 
						publisher_id = row[1],
						publisher_name = row[2],
						publisher_group = 'XXX'
					)
					pub.save()
			except Exception as error:
				err_flag = True
				print (error)
				err = Publisher_error (
					row_id = int(row[0]),
					publisher_id = row[1],
					publisher_name = row[2],
					error = error,
					created_date = datetime.datetime.now(),
					updated_date = datetime.datetime.now()		
				)
				err.save()				
				
			try:
				if publisher:
					published = True
				else:
					published = False
									
				## Get image file names
				pos = row[11].rfind('/')
				loc = 0
				if pos > 0:
					loc = pos+1
				url = row[11][loc:]
				####
				pos = row[12].rfind('/')
				loc = 0
				if pos > 0:
					loc = pos+1
				thumbnail_url = row[12][loc:]

				
				newprod = Stock_image(
					store = ecom,
					product_id = int(row[0]),
					name = row[4],
					description = '',
					price = 0,
					available_on = today,
					updated_at = today,
					part_number = row[3],
					product_type = prod_type,
					is_published = published,
					seo_description = '',
					seo_title  = '',
					charge_taxes = True,
					featured = False,
					has_variants = False,
					aspect_ratio = Decimal(row[6]) / Decimal(row[7]),
					image_type = row[9],
					orientation = row[8].strip().title(),
					max_width = row[6],
					max_height = row[7],
					min_width = 4,
					publisher = row[1],
					artist = row[5],
					colors = '',
					key_words = row[13],
					url = 'image_data/POD/images/' + url,
					thumbnail_url = 'image_data/POD/images/' + thumbnail_url			
				)

				newprod.save()

			except Exception as error:
				err_flag = True
				print (error)
				err = Stock_image_error (
					row_id = int(row[0]),
					name = row[4],
					error = error,
					created_date = datetime.datetime.now(),
					updated_date = datetime.datetime.now()		
				)
				err.save()
			'''					'''
			''' Categories 		'''
			'''					'''
			#get the category id
			prod_category = Stock_image_category.objects.filter(name__iexact = row[14]).first()
			if prod_category is None:
				# Insert
				try:
					prod_cat = Stock_image_category(
							store = ecom,
							name = row[14],
							description = '',
							background_image = '',
							parent = None,
							trending = False,
							url = '',
							featured_collection = False
					)
					prod_cat.save()
					prod_category = prod_cat

				except Exception as error:
					err_flag = True
					print (error)
					err = Stock_image_category_error (
						row_id = int(row[0]),
						category_name = row[14],
						error = error,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
				
			prod_prod_cat = Stock_image_stock_image_category.objects.filter(stock_image_id = row[0]).first()
			
			try:
				if prod_prod_cat :
					prod_cat = Stock_image_stock_image_category(
						id = prod_prod_cat.id,
						stock_image_id = row[0],
						stock_image_category = prod_category
					)
				else :
					prod_cat = Stock_image_stock_image_category(
						stock_image_id = row[0],
						stock_image_category = prod_category
					)
				prod_cat.save()				
				
			except Exception as error:
				err_flag = True
				print (error)
				err = Stock_image_stock_image_category_error (
					row_id = int(row[0]),
					stock_image_category = prod_category,
					error = error,
					created_date = datetime.datetime.now(),
					updated_date = datetime.datetime.now()		
				)
				err.save()
			'''
			publ_price = Publisher_price.objects.filter(publisher_id = row[1], 
				print_medium_id = 'PAPER').first()
				
			if not publ_price:
			
				pub_price = Publisher_price (
					publisher_id = row[1],
					print_medium_id = 'PAPER',
					price_type_id = 'SQIN',
					price = 10.50
				)

				pub_price.save()	

			publ_price = Publisher_price.objects.filter(publisher_id = row[1], 
				print_medium_id = 'CANVAS').first()
			if not publ_price:
			
				pub_price = Publisher_price (
					publisher_id = row[1],
					print_medium_id = 'CANVAS',
					price_type_id = 'SQIN',
					price = 12.50
				)

				pub_price.save()	
			'''
				
		cnt = cnt + 1
		
		#if cnt > 5000:
		#	break
				
	return 
	
	
def deletePODImageData():

	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	csvfile = urllib.request.urlopen(url)
	if csvfile.code != 200:
		print ("File not found on POD!")
		return
	cr = csv.reader(codecs.iterdecode(csvfile, 'utf-8'))

	# Get all products
	prods = Stock_image.objects.all()
	
	cnt = 0

	prod_ids = []
	for row in cr:	
		# Skip the first row (header)
		if cnt == 0:
			cnt = cnt + 1
			continue	
		prod_ids.append(row[0])

	for prod in prods:
		if str(prod.product_id) in prod_ids:
			None
		else:
			# Set product is_published to false
			if prod.product_id <= 1000000:
				prod = Stock_image.objects.filter(product_id = prod.product_id).update(
						is_published = False)
			print(cnt)
						
		cnt = cnt + 1
		if cnt >= 1000000:
			break	
	print("Total deleted: " + str(cnt) )
	return cnt
	
def downloadPODFile():
	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	csvfile = urllib.request.urlopen(url)
	if csvfile.code != 200:
		print ("File not found on POD!")
		return

	html = csvfile.read()

	with open('PODFile.csv', 'wb') as f:
			f.write(html)

def getPODImages():
	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	file = urllib.request.urlopen(url)
	if file.code != 200:
		print ("File not found on POD!")
		return
	
	cr = csv.reader(codecs.iterdecode(file, 'utf-8'))		
	#cr = csv.reader(csvfile, delimiter=',')

	cnt = 0
	for row in cr:
		# Skip the first row (header)
		cnt = cnt + 1
		if cnt == 0:
			continue

		if cnt < 10000:
			continue
			
		## Low Resolution Image
		lowres_url = row[11]
		pos = lowres_url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		lowres_img = lowres_url[loc:]
		file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img)
		# If file does not exists then copy the file
		if not file.is_file():	
			res = requests.get(lowres_url)
			img = Image.open(BytesIO(res.content))
			img.save("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img, 'JPEG')
		
		thumbnail_url = row[12]
		pos = thumbnail_url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		thumbnail_img = thumbnail_url[loc:]
		file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
		# If file does not exists then copy the file
		if not file.is_file():	
			res = requests.get(thumbnail_url)
			img = Image.open(BytesIO(res.content))
			img.save("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img, 'JPEG')

		if cnt%100 == 0:
			print( str(cnt/100) + ' images done...')
		
		if cnt >= 20000:
			break
		

def getPODImagesWget():
	import wget

	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	file = urllib.request.urlopen(url)
	if file.code != 200:
		print ("File not found on POD!")
		return
	
	cr = csv.reader(codecs.iterdecode(file, 'utf-8'))		
	#cr = csv.reader(csvfile, delimiter=',')

	cnt = 0
	img_dir = "/home/artevenue/website/estore/static/image_data/POD/images/"
	for row in cr:
		# Skip the first row (header)
		cnt = cnt + 1
		if cnt == 0:
			continue

		if cnt < 71000:
			continue
			
		## Low Resolution Image
		lowres_url = row[11]
		fl =  urllib.request.urlopen(lowres_url)
		if fl.code == 200:
			pos = lowres_url.rfind('/')
			loc = 0
			if pos > 0:
				loc = pos+1
			lowres_img = lowres_url[loc:]
			file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img)
			# If file does not exists then copy the file
			if not file.is_file():	
				print(lowres_url)
				wget.download(lowres_url, out=img_dir)
				
				#res = requests.get(lowres_url)
				#img = Image.open(BytesIO(res.content))
				#img.save("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img, 'JPEG')
			
		thumbnail_url = row[12]
		ft =  urllib.request.urlopen(thumbnail_url)
		if ft.code == 200:
			pos = thumbnail_url.rfind('/')
			loc = 0
			if pos > 0:
				loc = pos+1
			thumbnail_img = thumbnail_url[loc:]
			file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
			# If file does not exists then copy the file
			if not file.is_file():	
				print(thumbnail_url)
				wget.download(thumbnail_url, out=img_dir)

		if cnt%100 == 0:
			print( str(cnt/100) + ' images done...')
		
		if cnt >= 100000:
			break
		
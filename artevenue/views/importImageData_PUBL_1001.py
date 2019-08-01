from artevenue.models import Stock_image_category, Product_type, Tax
from artevenue.models import Stock_image, Stock_image_stock_image_category
from artevenue.models import Ecom_site, Publisher_price, Publisher, Generate_number
from artevenue.models import Stock_image_error, Stock_image_category_error, Publisher_error
from artevenue.models import Stock_image_stock_image_category_error
import csv

from django.contrib.staticfiles.templatetags.staticfiles import static
from datetime import datetime
import datetime
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from decimal import Decimal

ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
today = datetime.date.today()
PUBLISHER = '1001'
PUBLISHER_NAME = 'International Graphics'

def importNewPublisherData(): 
	file = 'C:/artevenue/DATA/POD_File/POD_file_1001.csv'
	
	cnt = 0

	prod_type = Product_type.objects.filter(product_type_id__iexact = "STOCK-IMAGE", store = ecom).first()

	prod_tax = Tax.objects.filter(name__iexact = "STOCK-IMAGE", store = ecom).first()
	tax_rate = prod_tax.tax_rate

	print("Starting...")
	import pdb
	pdb.set_trace()
	
	with open(file, encoding="ISO-8859-1") as csvfile:

		readCSV = csv.reader(csvfile, delimiter=',')

		
		for row in readCSV:
			# Skip the first row (header)
			if cnt == 0:
				cnt = cnt + 1
				continue
			
			# Skip the row if the the data is not valid for paper or canvas
			if row[11] != 'Y':
				cnt = cnt + 1
				continue				
				
			if row[0]:
				'''					'''
				''' Publisher 		'''
				'''					'''
				try:
					publisher = Publisher.objects.filter(publisher_id = PUBLISHER).first()
					if not publisher:
						pub = 	Publisher( 
							publisher_id = PUBLISHER,
							publisher_name = PUBLISHER_NAME,
							publisher_group = 'XXX'
						)
						pub.save()
				except Exception as error:
					err_flag = True
					print (error)
					err = Publisher_error (
						row_id = prod_id,
						publisher_id = PUBLISHER,
						publisher_name = PUBLISHER_NAME,
						error = error,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()



				orientation = 'Horizontal'
				if Decimal(row[16]) > Decimal(row[18]):
					orientation = 'Vertical'
				elif Decimal(row[16]) == Decimal(row[18]):
					orientation = 'Square'
				else :
					orientation = 'Vertical'
			
				# check if the image data already exists
				#prod = Stock_image.objects.filter(part_number = row[1]).first()
				try:
					prod_id = row[0]
					newprod = Stock_image(
						store = ecom,
						product_id = row[0],
						name = row[12],
						description = '',
						price = 0,
						available_on = today,
						updated_at = today,
						part_number = row[1],
						product_type = prod_type,
						is_published = True,
						seo_description = '',
						seo_title  = '',
						charge_taxes = True,
						featured = False,
						has_variants = False,
						aspect_ratio = Decimal(row[16]) / Decimal(row[18]),
						image_type = '0',
						orientation = orientation,
						max_width = row[16],
						max_height = row[18],
						min_width = 4,
						publisher = PUBLISHER,
						artist = row[13] + ' ' + row[14],
						colors = '',
						key_words = '',
						url = 'image_data/1001/images/' + row[3],
						thumbnail_url = 'image_data/1001/images/' + row[3]
					)
					newprod.save()
				except Exception as error:
					err_flag = True
					print (error)
					err = Stock_image_error (
						row_id = row[0],
						name = row[12],
						error = error,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
				'''					'''
				''' Categories 		'''
				'''					'''
				#get the category id
				prod_category = Stock_image_category.objects.filter(name__iexact = row[22]).first()
				if prod_category is None:
					# Insert
					try:
						prod_cat = Stock_image_category(
								store = ecom,
								name = row[22],
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
							row_id = row[0],
							category_name = row[22],
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
						row_id = row[0],
						stock_image_category = prod_category,
						error = error,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					
			cnt = cnt + 1
							
	return 
	

def getNextProdId(publ_id):
	prod_id = 0
	
	num_rec = Generate_number.objects.filter(type=publ_id).first()
	if num_rec :
		generated_num = num_rec.current_number + 1
	else :
		# Prod Id for new publisher starts from 500001
		generated_num = 500001
		
	# Update generated number in DB
	gen_num = Generate_number(
		type = type,
		description = "Publisher Image Number generation",
		current_number = generated_num
		)
	
	gen_num.save()
		
	return generated_num 	
	
		
	

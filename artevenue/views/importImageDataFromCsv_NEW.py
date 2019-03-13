from artevenue.models import Stock_image_category, Product_type, Tax
from artevenue.models import Stock_image, Stock_image_stock_image_category
from artevenue.models import Ecom_site, Publisher_price, Publisher
import csv

from django.contrib.staticfiles.templatetags.staticfiles import static
from datetime import datetime
import datetime
from django.shortcuts import render, get_object_or_404
from django.conf import settings

ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
today = datetime.date.today()

def importImageData_NEW(request): 

	file = 'C:/eCom_Platform/project/eComPlatform/eStore/static/image_data/pod_data.csv'
	#file = settings.STATIC_ROOT + '/image_data/pod_data.csv'
	
	cnt = 0
	'''Get Product type (IMAGE) '''
	prod_type = Product_type.objects.filter(product_type_id__iexact = "IMAGE", store = ecom).first()
	'''Get Tax code for IMAGE '''
	prod_tax = Tax.objects.filter(name__iexact = "STOCK-IMAGE", store = ecom).first()
	tax_rate = prod_tax.tax_rate

	with open(file, encoding="utf8") as csvfile:

		readCSV = csv.reader(csvfile, delimiter=',')

		
		for row in readCSV:
			# Skip the first row (header)
			if cnt == 0:
				cnt = cnt + 1
				continue
			if cnt < 81178:
				cnt = cnt + 1
				continue
			
				
			if row[0]:
				#prod = Product.objects.filter(product_id = int(row[0])).first()
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
					is_published = True,
					seo_description = '',
					seo_title  = '',
					charge_taxes = True,
					featured = False,
					has_variants = False,
					aspect_ratio = int(row[6]) / int(row[7]),
					image_type = row[9],
					orientation = row[8],
					max_width = row[6],
					max_height = row[7],
					min_width = 4,
					publisher = row[1],
					artist = row[5],
					colors = '',
					key_words = row[13],
					url = row[11],
					thumbnail_url = row[12]			
				)

				newprod.save()
						

				'''					'''
				''' Categories 		'''
				'''					'''
				#get the category id
				prod_category = Stock_image_category.objects.filter(name__iexact = row[14]).first()
				if prod_category is None:
					# Insert
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
				
				prod_prod_cat = Stock_image_stock_image_category.objects.filter(stock_image_id = row[0]).first()
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
					
				'''					'''
				''' Publisher Price '''
				'''					'''
				
				publisher = Publisher.objects.filter(publisher_id = row[1]).first()
				if not publisher:
					pub = 	Publisher( 
						publisher_id = row[1],
						publisher_name = row[2],
						publisher_group = 'XXX'
					)
					pub.save()

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
				
	return render(request, "artevenue/import_image_data.html")
	
	
def deleteRemovedImageData(request):

	# Get all products
	prods = Product.objects.all().values('product_id')
	
	file = 'C:/eCom_Platform/project/eComPlatform/artevenue/static/image_data/pod_data.csv'
	cnt = 0

	with open(file, encoding="utf8") as csvfile:

		readCSV = csv.reader(csvfile, delimiter=',')

		
		for row in readCSV:	
			if int(row[0]) in prods:
				None
			else:
				# Set product is_published to false
				prod = Product(
						store = ecom,
						product_id = int(row[0]),
						name = row[4],
						description = '',
						price = 0,
						available_on = today,
						updated_at = today,
						part_number = row[3],
						product_type = prod_type,
						is_published = False,
						charge_taxes = True,
						tax = prod_tax,
						tax_rate = tax_rate,
						featured = False,
						has_variants = False,
						size = None,
						default_frame = None
					)
				prod.save()
					
				
			
			cnt = cnt + 1
			print(cnt)
		
	return render(request, "artevenue/delete_image_data.html")
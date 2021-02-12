from artevenue.models import Product_view, Moulding, Moulding_image
from artevenue.models import Curated_collection, Mount
from artevenue.models import Amazon_data, Stock_image_stock_image_category
from gallerywalls.models import Gallery, Gallery_variation, Gallery_item
from django.conf import settings
from decimal import Decimal

from PIL import Image, ImageFilter, ImageFile
import requests
from .product_views import *
from .tax_views import *
from .price_views import *
from artevenue.views import *
from gallerywalls.views import *

import requests
from io import BytesIO

abstract_ids = [262896, 232351, 232388, 165919, 261963, 247687, 255442, 42812, 166669, 158023, 158056, 158202, 158336, 263380, 170384, 270431]
floral_ids = [226075, 201564, 190019, 208356, 221431, 221455, 246608, 270667, 206199, 157659, 157702, 157695, 219906, 237062, 166523, 283351, 254978, 315771]
landscape_ids = [246554, 304861, 270707, 232260, 220231, 204619, 19045, 236818, 246312, 264975, 226611, 275667, 218493, 281025, 255026, 255755, 255765]


def createABdata():
	av_createAmazonData("ABSTRACT", abstract_ids)	
	av_createAmazonImages("ABSTRACT", abstract_ids)
	av_createAmazonFile("ABSTRACT", abstract_ids)
	
def createFLdata():
	av_createAmazonData("FLORAL", floral_ids)
	av_createAmazonImages("FLORAL", floral_ids)
	av_createAmazonFile("FLORAL", floral_ids)
	
def createLDdata():
	av_createAmazonData("LANDSCAPE", landscape_ids)
	av_createAmazonImages("LANDSCAPE", landscape_ids)
	av_createAmazonFile("LANDSCAPE", landscape_ids)

def createABFile():
	av_createAmazonFile("ABSTRACT", abstract_ids)
def createFLFile():
	av_createAmazonFile("FLORAL", floral_ids)
def createLDFile():
	av_createAmazonFile("LANSDACPE", landscape_ids)


def createAllCuratedData():
	ids = abstract_ids + floral_ids + landscape_ids
	ids = Amazon_data.objects.all().values('products_id')
	av_createAmazonData('CURATED', ids)	
	av_createAmazonImages("CURATED", ids)
	

def createAllData():
	#ids = Amazon_data.objects.filter(amazon_key__gte = 161661).values('product_id')
	av_createAmazonData('ALL')	
	av_createAmazonImages("ALL")

def createAdsData():
	#ids = Amazon_data.objects.filter(amazon_key__gte = 161661).values('product_id')
	cfile = Path('/home/artevenue/website/estore/static/feeds/amazon/ad_prods.csv')
	if not cfile.is_file():
		print("ad_prods.csv file did not downloaded")
		return
	file = open('/home/artevenue/website/estore/static/feeds/amazon/ad_prods.csv')	
	cr = csv.reader(file, delimiter=',')
	prods_list = []
	for row in cr:
		prods_list.append(row[0])
	
	if not prods_list:
		print("No rows in ad_prods.csv")
		return	
		
	#av_createAmazonData('ADS', prods_list)	
	#av_createAmazonImages("ADS", prods_list)
	av_createAmazonFile("ADS", prods_list)

def av_createAmazonData(cat, ids):
	cnt = 0
	if cat == "ABSTRACT":
		sku_suf = "AVA"
		sku_int = 10000  ## for Abstract
	if cat == "FLORAL":
		sku_suf = "AVF"
		sku_int = 10000  ## for Floral
	if cat == "LANDSCAPE":
		sku_suf = "AVL"
		sku_int = 10000  ## for Landscape
	if cat == 'CURATED':
		sku_suf = "ACU"
		sku_int = 10000  ## for Landscape
	if cat == 'ALL':
		sku_suf = "AA"
		sku_int = 59972  ## for Landscape
	if cat == 'ADS':
		sku_suf = "AA"
		sku_int = 70000  ## Ad prods


	#### Get all curated category products, except for the ones already processed
	##prods = Curated_collection.objects.all().exclude(product_id__in = ids)
	excl_ids = Amazon_data.objects.all().values('product_id')
	##prods = Stock_image.objects.all().exclude(product_id__in = ids)
			## Cat "ALL":   2nd Set (1st set 0:1000, 2nd set 1001:3000 - DONE)
	prods = Stock_image.objects.filter(product_id__in = ids).exclude(
		product_id__in = excl_ids).order_by('product_id')
	#for c in ids:
	for cprd in prods:
		cnt = cnt + 1
		prod = Product_view.objects.filter(product_id = cprd.product_id, product_type_id = 'STOCK-IMAGE').first()
		if prod:
			print("Processing: " + str(prod.product_id))
			if prod.is_published == False:
				continue

			if not prod:
				print( "No product found: ID = " + str(prod.product_id) )
				return

			## Check if this product is already processed
			p = Amazon_data.objects.filter(product_id = prod.product_id).first()
			if p:
				print( "Product = " + str(prod.product_id)  + " is already processed, skipping")
				continue
			
			category = Stock_image_stock_image_category.objects.get(
				stock_image_id = prod.product_id)
			category_id = category.stock_image_category_id
			quantity = 1
			
			#####################################################
			# Generate Amazon SKU Number
			#####################################################
			sku_int = sku_int + 1
			parent_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Amazon SKU Number
			#####################################################

			#########################################################
			## Create parent record first
			#########################################################
			hl = Amazon_data(
				amazon_sku = parent_sku,
				product_id = prod.product_id,
				product_name = prod.name,
				description = prod.description,
				part_number = prod.part_number,
				product_type = prod.product_type,
				category = category.stock_image_category,
				category_name = category.stock_image_category.name,
				is_published = prod.is_published,
				aspect_ratio = prod.aspect_ratio,
				image_type = prod.image_type,
				orientation = prod.orientation,
				max_width = prod.max_width,
				max_height = prod.max_height,
				min_width = prod.min_width,
				publisher = prod.publisher,
				artist = prod.artist,
				colors = prod.colors,
				key_words = prod.key_words,
				url = prod.url,
				thumbnail_url = prod.thumbnail_url,
				framed_url = '',
				framed_thumbnail_url = '',
				promotion = None,
				promotion_name = '',
				quantity = 1000,
				item_unit_price = 1000,
				item_sub_total = 1000,
				item_disc_amt  = 0,
				item_tax  = 120,
				item_total = 1200,
				moulding = None,
				moulding_name = '',
				moulding_size = 0,
				print_medium_id = 'PAPER',
				print_medium_name = '',
				print_medium_size = 0,
				mount = None,
				mount_name = '',
				mount_size = 0,
				board_id = None,
				board_name = '1',
				board_size = 0,
				acrylic_id = None,
				acrylic_name = '1',
				acrylic_size = 0,
				stretch_id = None,
				stretch_name = '1',
				stretch_size = 0,
				image_width = 16,
				image_height = 16,
				created_date = today,
				updated_date = today,
				parent_child = 'P',
				parent_amz_sku = ''
			)
			hl.save()		
			

			
			#########################################################
			## Create 5 versions with different sizes
			#########################################################
			if prod.aspect_ratio > 1:
				h = 10
				w = round(h * prod.aspect_ratio)
				STANDARD_PROD_WIDTHS = [w, w+4 , w+8, w+12, w+16, w+20]
			else:
				STANDARD_PROD_WIDTHS = [10, 14, 18, 22, 26, 30]

			for size in STANDARD_PROD_WIDTHS:		
				'''
				if prod.orientation == 'Vertical' or prod.orientation == 'Square':
					img_width = size
					img_height = round(img_width / prod.aspect_ratio)
				else:
					img_height = size
					img_width = round(img_height * prod.aspect_ratio)			
				'''
				img_width = size
				img_height = round(img_width / prod.aspect_ratio)

				if img_width > 40 and img_height > 40:
					continue

				#########################################################
				## Moulding and Mount for for framed 
				#########################################################
				moulding_id = 18 # Simple Black					
				moulding = Moulding.objects.get( moulding_id = moulding_id )
				moulding_name = ''
				if moulding:
					moulding_name = moulding.name

				mount = Mount.objects.get(pk=1)   ## Offwhite
				mount_color = ''
				if mount :
					mount_color = mount.color
			
				if img_width <= 18 or img_height < 18:
					mount_size = 1
				else:
					mount_size = 2
					
				#####################################################
				## With frame PAPER
				#####################################################
				#         Get the item price
				price = get_prod_price(prod.product_id, 
						prod_type= prod.product_type_id,
						image_width=img_width, 
						image_height=img_height,
						print_medium_id = 'PAPER',
						acrylic_id = 1,
						moulding_id = moulding_id,
						mount_size = mount_size,
						mount_id = mount.mount_id,
						board_id = 1,
						stretch_id = 0)
				item_price = price['item_price']
				msg = price['msg']
				cash_disc = price['cash_disc']
				percent_disc = price['percent_disc']
				item_unit_price = price['item_unit_price']
				item_disc_amt = price['disc_amt']
				disc_applied = price['disc_applied']
				promotion_id = price['promotion_id']
				# END::::    Get the item price
				
				# 	if item price not found, return
				if item_unit_price == 0 or item_unit_price is None:
					err_flg = True
					return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_quantity':quantity}, safe=False) )
				# END:	if item price not found, don't add to cart

				## Increase price by 20%, to manage the returns			##################################################
				item_price = item_price + round((item_price*20/100))
				
				
				#	Calculate sub total, tax for the item
				item_tax = 0
				item_sub_total = 0
				#### Get Tax
				taxes = get_taxes()
				if prod.product_type_id == 'STOCK-IMAGE':
					tax_rate = taxes['stock_image_tax_rate']
				if prod.product_type_id == 'ORIGINAL-ART':
					tax_rate = taxes['original_art_tax_rate']
				if prod.product_type_id == 'USER-IMAGE':
					tax_rate = taxes['user_image_tax_rate']
				if prod.product_type_id == 'STOCK-COLLAGE':
					tax_rate = taxes['stock_image_tax_rate']
				if prod.product_type_id == 'FRAME':
					tax_rate = taxes['frame_tax_rate']	
					
				# Calculate tax and sub_total
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item
				

				# 	Get the product promotion details, if the item carries it
				promo = {}
				if prod:
					promo = get_product_promotion(prod.product_id)	
				promotion = None
				if promo :
					if promo['promotion_id']:
						promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
				# END:	Get the product promotion, if the item carries it			
				
				# Generate Amazon SKU Number
				sku_int = sku_int + 1
				amz_sku = sku_suf + str(sku_int)
				# END: Generate Amazon SKU Number
				
				# Create Amazon DATA
				## Insert or Update
				promo_name = ''
				if promotion:
					promo_name = promotion.name
				hl = Amazon_data(
					amazon_sku = amz_sku,
					product_id = prod.product_id,
					product_name = prod.name,
					description = prod.description,
					part_number = prod.part_number,
					product_type = prod.product_type,
					category = category.stock_image_category,
					category_name = category.stock_image_category.name,
					is_published = prod.is_published,
					aspect_ratio = prod.aspect_ratio,
					image_type = prod.image_type,
					orientation = prod.orientation,
					max_width = prod.max_width,
					max_height = prod.max_height,
					min_width = prod.min_width,
					publisher = prod.publisher,
					artist = prod.artist,
					colors = prod.colors,
					key_words = prod.key_words,
					url = prod.url,
					thumbnail_url = prod.thumbnail_url,
					framed_url = '',
					framed_thumbnail_url = '',
					promotion = promotion,
					promotion_name = promo_name,
					quantity = quantity,
					item_unit_price = item_unit_price,
					item_sub_total = item_sub_total,
					item_disc_amt  = item_disc_amt,
					item_tax  = item_tax,
					item_total = item_price,
					moulding = moulding,
					moulding_name = moulding.name,
					moulding_size = 0,
					print_medium_id = 'PAPER',
					print_medium_name = 'PAPER',
					print_medium_size = 0,
					mount = mount,
					mount_name = mount_color,
					mount_size = mount_size,
					board_id = 1,
					board_name = '1',
					board_size = 0,
					acrylic_id = 1,
					acrylic_name = '1',
					acrylic_size = 0,
					stretch_id = 1,
					stretch_name = '1',
					stretch_size = 0,
					image_width = img_width,
					image_height = img_height,
					created_date = today,
					updated_date = today,
					parent_child = 'C',
					parent_amz_sku = parent_sku
				)
				hl.save()		


				#####################################################
				## With frame CANVAS
				#####################################################
				#         Get the item price
				price = get_prod_price(prod.product_id, 
						prod_type= prod.product_type_id,
						image_width=img_width, 
						image_height=img_height,
						print_medium_id = 'CANVAS',
						acrylic_id = 1,
						moulding_id = moulding_id,
						mount_size = 0,
						mount_id = 0,
						board_id = 1,
						stretch_id = 1)
				item_price = price['item_price']
				msg = price['msg']
				cash_disc = price['cash_disc']
				percent_disc = price['percent_disc']
				item_unit_price = price['item_unit_price']
				item_disc_amt = price['disc_amt']
				disc_applied = price['disc_applied']
				promotion_id = price['promotion_id']
				# END::::    Get the item price
				
				# 	if item price not found, return
				if item_unit_price == 0 or item_unit_price is None:
					err_flg = True
					return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_quantity':quantity}, safe=False) )
				# END:	if item price not found, don't add to cart

				## Increase price by 15%, to manage the returns
				item_price = item_price + round((item_price*20/100))
				
				
				#	Calculate sub total, tax for the item
				item_tax = 0
				item_sub_total = 0
				#### Get Tax
				taxes = get_taxes()
				if prod.product_type_id == 'STOCK-IMAGE':
					tax_rate = taxes['stock_image_tax_rate']
				if prod.product_type_id == 'ORIGINAL-ART':
					tax_rate = taxes['original_art_tax_rate']
				if prod.product_type_id == 'USER-IMAGE':
					tax_rate = taxes['user_image_tax_rate']
				if prod.product_type_id == 'STOCK-COLLAGE':
					tax_rate = taxes['stock_image_tax_rate']
				if prod.product_type_id == 'FRAME':
					tax_rate = taxes['frame_tax_rate']	
					
				# Calculate tax and sub_total
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item
				

				# 	Get the product promotion details, if the item carries it
				promo = {}
				if prod:
					promo = get_product_promotion(prod.product_id)	
				promotion = None
				if promo :
					if promo['promotion_id']:
						promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
				# END:	Get the product promotion, if the item carries it
				
				# Generate Amazon SKU Number
				sku_int = sku_int + 1
				amz_sku = sku_suf + str(sku_int)
				# END: Generate Amazon SKU Number

				# Create Amazon DATA
				## Insert or Update
				promo_name = ''
				if promotion:
					promo_name = promotion.name
				hl = Amazon_data(
					amazon_sku = amz_sku,
					product_id = prod.product_id,
					product_name = prod.name,
					description = prod.description,
					part_number = prod.part_number,
					product_type = prod.product_type,
					category = category.stock_image_category,
					category_name = category.stock_image_category.name,
					is_published = prod.is_published,
					aspect_ratio = prod.aspect_ratio,
					image_type = prod.image_type,
					orientation = prod.orientation,
					max_width = prod.max_width,
					max_height = prod.max_height,
					min_width = prod.min_width,
					publisher = prod.publisher,
					artist = prod.artist,
					colors = prod.colors,
					key_words = prod.key_words,
					url = prod.url,
					thumbnail_url = prod.thumbnail_url,
					framed_url = '',
					framed_thumbnail_url = '',
					promotion = promotion,
					promotion_name = promo_name,
					quantity = quantity,
					item_unit_price = item_unit_price,
					item_sub_total = item_sub_total,
					item_disc_amt  = item_disc_amt,
					item_tax  = item_tax,
					item_total = item_price,
					moulding = moulding,
					moulding_name = moulding.name,
					moulding_size = 0,
					print_medium_id = 'CANVAS',
					print_medium_name = 'CANVAS',
					print_medium_size = 0,
					mount = None,
					mount_name = None,
					mount_size = None,
					board_id = None,
					board_name = '1',
					board_size = 0,
					acrylic_id = None,
					acrylic_name = '1',
					acrylic_size = 0,
					stretch_id = None,
					stretch_name = '1',
					stretch_size = 0,
					image_width = img_width,
					image_height = img_height,
					created_date = today,
					updated_date = today,
					parent_child = 'C',
					parent_amz_sku = parent_sku
				)
				hl.save()		
	
	print("Data creation/Update complete: Count - " + str(cnt) )


def av_createAmazonImages(cat=None, ids=None):

	#if not i_ids:
	#	i_ids = abstract_ids + floral_ids + landscape_ids

	if not cat:
		cat = 'ALL'
		
	#### Get all curated category products, except for the ones already processed
	#prods = Curated_collection.objects.all().exclude(product_id__in = i_ids)	
	#prods = Stock_image.objects.all().exclude(product_id__in = i_ids)[:1000]
	
	#ids = prods.values('product_id')
	
	amazon_data = Amazon_data.objects.filter(is_published = True,
	amazon_key__gt = 171644, product_id__in = ids).order_by('product_id')
	
	for h in amazon_data:
		if h.product_id <= 1000:
			continue
			
		print("Processing: " + str(h.amazon_key))
				
		if h.parent_child == 'P':
			image_width = 16
		else:
			image_width = float(h.image_width)
	
		if h.moulding:
			if h.mount:
				framed_img = get_amz_FramedImage_api(h.product_id, h.moulding_id, 
					h.mount.color, float(h.mount_size), image_width)
			else:
				framed_img = get_amz_FramedImage_api(h.product_id, h.moulding_id, 
					None, 0, image_width)
				
			f_nm = "f_"
		else:
			framed_img = get_amz_FramedImage_api(h.product_id)
			f_nm = "n_"
			
		env = settings.EXEC_ENV
		img_url = ''
		if env == 'DEV' or env == 'TESTING':
			img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "amazon_data/images/" 
			img_url = img_loc
		else:
			img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "amazon_data/images/"
			img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "amazon_data/images/"
		
		pos = h.url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		lowres_img_name = h.amazon_sku +"_" + h.url[loc:]
		
		# save image
		ifile = Path(img_loc + lowres_img_name)
		if ifile.is_file():
			print("Image already available...skipping - Main image")
		else:
			framed_img.save(img_loc + lowres_img_name)
		
		## Generate card images only for child rows
		if h.parent_child == 'C':
			if h.moulding_id :
				m_id = h.moulding_id
				if h.mount:
					mnt_color = h.mount.color
					mnt_size = float(h.mount_size)
				else:
					mnt_color = '0'
					mnt_size = 0
			else:
				m_id = '0'
				mnt_color = '0'
				mnt_size = 0				

			#######################################################
			from django.http import HttpRequest
			request = HttpRequest()
			
			request.GET['prod_id'] = h.product_id
			request.GET['moulding_id'] = m_id
			request.GET['mount_color'] = mnt_color

			request.GET['mount_size'] = mnt_size
			request.GET['image_width'] = h.image_width
			request.GET['prod_type'] = h.product_type_id

			## Card 1
			request.GET['card_no'] = '1'
			card = get_catalog_card(request, False)
			low_res_card1 = h.amazon_sku +"_card1_" + h.url[loc:]
			# save image
			c1file = Path(img_loc + low_res_card1)
			if c1file.is_file():
				print("Image already available...skipping - Card 1")
			else:
				card.save(img_loc + low_res_card1)
			
			## Card 2
			#request.GET['card_no'] = '2'
			#card = get_catalog_card(request, False)
			#low_res_card2 = h.amazon_sku +"_card2_" + h.url[loc:]
			#c2file = Path(img_loc + low_res_card2)
			#if c2file.is_file():
			#	print("Image already available...skipping - Card 2")
			#else:
			#	card.save(img_loc + low_res_card2)

			## Card 3
			#request.GET['card_no'] = '3'
			#card = get_catalog_card(request, False)
			#low_res_card3 = h.amazon_sku +"_card3_" + h.url[loc:]
			#c3file = Path(img_loc + low_res_card3)
			#if c3file.is_file():
			#	print("Image already available...skipping - Card 3")
			#else:
			#	card.save(img_loc + low_res_card3)
			
			## Card 4
			#request.GET['card_no'] = 'AMZ_C1'
			#card = get_catalog_card(request, False)
			#low_res_card4 = h.amazon_sku +"_card5_" + h.url[loc:]
			#c4file = Path(img_loc + low_res_card1)
			#if c4file.is_file():
			#	print("Image already available...skipping - Card 4")
			#else:
			#	card.save(img_loc + low_res_card4)
			
		if h.parent_child == 'C':
			## Save in urls table
			hf = Amazon_data.objects.filter(amazon_key = h.amazon_key).update(	
					framed_url = img_url + lowres_img_name,
					card1_url = img_url + low_res_card1, 
					card2_url = 'https://www.artevenue.com/static/img/catalog/amz_f_card.jpg'
					#card2_url = img_url + low_res_card2,
					#card3_url = img_url + low_res_card4 
					)  #card4_url = img_url + low_res_card4
		else:
			## Save in urls table
			hf = Amazon_data.objects.filter(amazon_key = h.amazon_key).update(	
					framed_url = img_url + lowres_img_name)			
			
		print("Saved: " + lowres_img_name)
		
		
def av_createAmazonFile(icat=None, ids=None):
	if not ids:
		ids = abstract_ids + floral_ids + landscape_ids

	if not icat:
		icat = "ALL"
	#### Get all curated category products, except for the ones already processed
	#prods = Curated_collection.objects.all().exclude(product_id__in = ids)
	#ids = prods.values('product_id')
	
	amz = Amazon_data.objects.filter(is_published = True,
		amazon_key__gt = 171644, product_id__in = ids).order_by('amazon_key')
	
	print("COUNT: " + str(amz.count()) )
	#cat = cat.title()
	#amz = Amazon_data.objects.filter(is_published = True, product_id__in = ids).order_by('amazon_sku')
		
	file_nm = 'av_amz_data_' + icat + '.csv'
	
	with open(file_nm, 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row =['product_type', 'Seller SKU', 'Brand', 'Product ID', 'Product ID Type',
			'Item Name', 'Manufacturer', 'Manufacturer Part Number', 'Recommended Browse Nodes', 
			'model', 'Color Map', 'Size', 'Included Components', 
			'Enclosure Material', 'Is Assembly Required', 'Item Type Name', 'Manufacturer Contact',
			'Item Heigh', 'Item Length', 'Item Width', 'unit Count', 'Item dimensions Unit of Measure',
			'Unit Count Type', 'Country Of Origin', 'Standard Price', 'Quantity', 'Maximum Retail Price',
			'Main Image URL',
			
			## Images
			'Other Image URL1', 'Other Image URL2', 'Other Image URL3', 'Other Image URL4',
			'Other Image URL5', 'Other Image URL6', 'Other Image URL7', 'Other Image URL8',
			'Swatch Image URL', 
			
			## Variation
			'Relationship Type', 'Variation Theme', 'Parent SKU', 'Parentage',
			  
			## Basic
			'Update Delete', 'Manufacturer', 'Description', 'Product Care Instructions',

			## Discovery
			'Search Terms', 'Bullet Point1', 'Bullet Point2', 'Bullet Point3',
			'Bullet Point4', 'Bullet Point5', 'color Name',	'Occassion', 'Finish', 
			'Pattern', 
			'Product Features1', 'Product Features2', 'Product Features3',
			'Product Features4', 'Product Features5', 'Style', 'Scent', 'Power Source',
			'Packer', 'Target Audience', 'lemght_range', 'Importer', 'Frame Type',
			'Theme', 'Department',
						
			## Diamesions
			'Shipping Weight',
			'Website Shipping Weight Unit of Measure', 'Shape', 'Item Volume', 'Item Volume Unit of Measure',
			'item Weight', 'Item Weight Unit of Measure', 'Display Volume', 'Item Display Width Unit of Measure',
			'Display Weight', 'Item Display Weight Unit of Measure', 'Display Width', 'Item Height Unit of Measure',
			'Display Depth', 'Item Display Depth Unit of Measure', 'Item Height', 
			'Item Display diameter', 'Size Map', 'Width Range', 'Item Display Diameter Unit of Measure',
			'Item Display Depth of Measure', 'Display Length', 'Display Length Unit of Measure',
			'Outside Diameter Delivered', 'Item Diameter Unit of Measure',
			

			#Compliance
			'Batteries are Included', 'Battary Type/Size 1', 'Battary Type/Size 2', 
			'Number of Batteries 1',  'Number of Battaries 2', 
			'Number of Batteries 3', 'Warranty Description', 'Safety Warning', 'Legal Disclaimer',
			'Is This Product a Battery or uses Battery?', 'Battery Comosition', 
			'Number of Lithium Metal Cells', 'Lithium Battery Packaging', 
			'Watt Hours per Battery', 'Lithium Battery Energy Content Unit of Measure',
			'Lithium Content', 'Lithium Battery Content', 'Lithium Battery Weigth Unit of Measure', 
			'Specific Uses of Product', 'HSN Code', 

			## Offer
			'Handling Time', 'Item Condition', 'Offer Condition Note', 'Launch Date', 'Release Date',
			'Number of Items', 'Item Package Quantity', 'Sale Start Date', 'Sale End Date', 
			'Sale Price', 'Restock Date', 'Is Giftwrap Avaiable?', 'Can Gift be Messaged?',
			'Is Discontinued by Manufacturer', 'Product Tax Code', 'Max Order Quantity', 
			'Offer End Date', 'Shipping-Template', 'Offer Start Date',

			##B2B
			'Business Price', 'Quantity Price Type', 'Quantity Price 1', 'Quantity Lower Bound 1',
			'Quantity Price 2', 'Quantity Lower Bound 2', 'Quantity Price 3', 'Quantity Lower Bound 3',
			'Quantity Price 4', 'Quantity Lower Bound 4', 'Quantity Price 5', 'Quantity Lower Bound 5',
			'Pricing Action'

			]
		wr.writerow(row)
		for h in amz:
			print("processing..." + str(h.amazon_key) )
			length = formatNumber(h.image_height) 
			if h.moulding:
				if h.moulding.width_inner_inches:
					length = formatNumber(length + (h.moulding.width_inner_inches * 2))
				if h.mount:
					if h.mount_size:
						length = formatNumber(length + (h.mount_size * 2))
			
			breadth = formatNumber(h.image_width)
			if h.moulding:
				if h.moulding.width_inner_inches:
					breadth = formatNumber(breadth + (h.moulding.width_inner_inches * 2))
				if h.mount:
					if h.mount_size:
						breadth = formatNumber(breadth + (h.mount_size * 2))

			
			cat = h.category_name.title()

			prod_details = cat + " Painting with frame," + " Title: " + h.product_name + ", Artist: " + h.artist + ".\nPrinted on: " + h.print_medium_id.title() + "; Framed Art Print. "
			prod_details = prod_details + "Image Size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + "; \n"
			incl_components = "One piece " + cat + " art with frame, printed on " + h.print_medium_id.title() + "; "
			incl_components = incl_components + "Image Print Size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + "; "
			if h.print_medium_id == 'PAPER':
				if h.moulding_id:
					bullet1 = 'Printed on ' + h.print_medium_id.title() + ', size: ' + str(formatNumber(h.image_width + (h.moulding.width_inner_inches *2) + (h.mount_size *2) )) + " X " + str(formatNumber(h.image_height + (h.moulding.width_inner_inches * 2) + ( h.mount_size * 2) )) + " inch. "
				else:
					bullet1 = "Printed on " + h.print_medium_id.title() + ", size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + " inch. "
				prod_details = prod_details + "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
			else:
				if h.moulding_id:
					bullet1 = 'Printed on ' + h.print_medium_id.title() + ', size: ' + str(formatNumber(h.image_width + (h.moulding.width_inner_inches *2) )) + " X " + str(formatNumber(h.image_height + (h.moulding.width_inner_inches * 2) )) + " inch. "
				else:
					bullet1 = "Printed on " + h.print_medium_id.title() + ", size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + " inch. "
				prod_details = prod_details + "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \n"
			bullet2 = ''
			t_size = ''
			if h.moulding_id:
				prod_details = prod_details + "Frame: " + h.moulding.name + " (" + str(formatNumber(h.moulding.width_inches)) + " inch). Frame is made of polystyrene, which is light weight, long lasting and has very good finish. \n"
				incl_components = incl_components + "Frame: " + h.moulding.name + " (" + str(formatNumber(h.moulding.width_inches)) + " inch, Polystyrene). "
				bullet2 = "Frame: " + h.moulding.name + " (" + str(formatNumber(h.moulding.width_inches)) + " inch). It's a high quality frame made of Polystyrene, which is light weight, long lasting and has very good finish. \n" 
			if h.mount_id:
				prod_details = prod_details + "Mount: " + str(formatNumber(h.mount_size)) + " inch, Color: " + h.mount.name.lower() + ", it enhances the look of this artwork. \n"
				incl_components =  incl_components + "Mount: " + str(formatNumber(h.mount_size)) + " inch, Color: " + h.mount.name.lower() + ". "
				bullet2 = bullet2 + ", " +str(formatNumber(h.mount_size)) + " inch " + h.mount.name.lower() + " mount adds classy look to this art. "
			## Total Size
			t_size_width = h.image_width
			t_size_height = h.image_height
			if h.moulding:
				if h.moulding.width_inner_inches:
					t_size_width = t_size_width + h.moulding.width_inner_inches *2
					t_size_height = t_size_height + h.moulding.width_inner_inches *2
			if h.mount:
				t_size_width = t_size_width + h.mount_size*2
				t_size_height = t_size_height + h.mount_size*2
			
			t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
			prod_details = prod_details + "Product Size (with frame): " + t_size
			incl_components = incl_components + "Product Size  (with frame): " + t_size
			
			bullet3 = ''
			if h.print_medium_name == "PAPER":
				if h.acrylic_id:
					prod_details = prod_details + "\nThe artwork is covered with clear acrylic for added protection, durability and clear visibility. Acrylic is light weight and durable."
					incl_components = incl_components + "Acrylic covered; "
				bullet3 = "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility."
			else:
				bullet3 = "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions."
				
			#if i.stretch_id:
			#	prod_details = prod_details +  + "Canvas Stretched; "

			search_terms = ( cat + " paintings, wall paintings, wall art, paintings for home decor, art print, paintings with frame, paintings for living room, paintings for bed room, wall decor " + h.key_words.replace('|', ', '))[:150]
			
			## Convert to upper case and remove duplicate words, limit to 150 chars
			##search_terms = ' '.join(set(search_terms.upper().split()))[:150]
			
			parentSKU = h.parent_amz_sku
			parent_child = h.parent_child
			if parent_child == 'P' or parent_child == '' or parent_child is None:
				parentage = 'Parent'
				variation = ''
				col = ''
				col_map = 'Multi-coloured'
				p_size = 'Size: ' + str(10) + '" X ' + str(10) + '" (inches)'
				size_map = ''
				qty = '1'
				item_total = 0
				parent_amz_sku = ''
			else:
				parentage = 'Child'
				variation = 'Variation'
				col = 'Multi'
				col_map = 'Multi-coloured'
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Print on ' + h.print_medium_id.title()
				size_map = 'Medium'
				qty = '1000'
				item_total = h.item_total
				parent_amz_sku = h.parent_amz_sku
			
			item_total_mrp = round(item_total + (item_total * 20 /100))
			
			prod_name =  cat + " painting with frame, Title: " + h.product_name + "; Framed Art Print on "  + h.print_medium_id.title() + "; (" + t_size + ") | Arte'Venue"

			update_delete = "Update"
			if h.image_width > h.max_width or h.image_height > h.max_height:
				update_delete = "Delete"
			
			color_name = ''
			occassion = ''
			finish_type = 'Matt finish'
			pattern_name = ''
			style_name = cat
			scent_name = ''
			power_source_type = ''
			packer_contact_information = ''
			target_audience_base = ''
			length_range = ''
			importer_contact_information = ''
			frame_type = 'Hanging'
			theme = ''
			department = ''
			item_volume = ''
			display_volume = ''
			
			t_size = t_size_width * t_size_height
			if t_size <= 256:
				ship_weight = 1.5
			elif t_size <= 576:
				ship_weight = 2
			elif t_size <= 900:
				ship_weight = 2.5
			elif t_size <= 1600:
				ship_weight = 3
			else:
				ship_weight = 3.5
	
			item_display_weight = ship_weight
				
			row =['furnitureanddecor', h.amazon_sku, "ARTE'VENUE", 
					'', '', prod_name, 'Montage Art Pvt Ltd', h.part_number, '3749951031', h.part_number,
					col_map, p_size, incl_components, 'Others',
					'Framed Wall Art for Home Decor', 'false', 'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',
					str(formatNumber(t_size_height)), str(formatNumber(t_size_width)), 2,
					1, 'inches', 'Unit', 'India', item_total, qty, 
					item_total_mrp, h.framed_url,
					
					##Images
					h.card1_url, h.card2_url, h.card3_url, h.card4_url, h.card5_url,
					'', '', '', '',
					
					## Variation
					variation, 'Size', parent_amz_sku, parentage,  
					
					## Basic Info
					update_delete, prod_details, "Wipe with soft, clean and dry cloth. No special care required.",
					
					## Discovery
					search_terms, 
					'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
					bullet1, bullet2, bullet3, 
					'Custom made for you. Comes with hooks and is ready to be hung on the wall.', 
					color_name, occassion, finish_type, pattern_name, 					
					"", "", "", "", "", 
					style_name, scent_name, power_source_type, packer_contact_information,
					target_audience_base, length_range, importer_contact_information,
					frame_type, theme, department,
					
					## - Diamensions
					ship_weight, 'KG', 'Square/Rectangular', item_volume, '', 
					ship_weight, 'KG', display_volume, '', item_display_weight, 'KG', 
					str(t_size_width + 3), 'IN', 8, 'IN', str(t_size_height + 3), '', size_map, '', '', 'IN', 
					8, 'IN', '', '',

					##-- Compliance
					'FALSE', "", "", "", "", "", "", 'Carries no warranties', '', 
					'Customized product. Return/Refund in case of damaged product delivery. The colors seen and product sizes specificed may change slightly.',
					'FALSE', '', '', '', '',  '', '', '', '',
					'Wall Decor', '',
					
					##-- Offer
					'2', 'New', '', '', '', '1', '1' ,'2020-12-01' ,'2021-06-30' , item_total, '', 'FALSE','',
					 '', '', '', '', '', '', '', 
					
					##-- B2B
					'', '', '', '', '', '', '', '' , '', '',
					'', '', ''

					#"", "", str(breadth*2.65), "CM", str(length*2.65), "CM", str(4*2.65), "CM" , str(itm_weight), "KG",
					
				]
				
			wr.writerow(row)



def av_createGwFile():
	sku_int = 10000
	sku_suf = 'AGW'

	gfile = "amz_gallery_walls.csv"
	with open(gfile, 'w', newline='') as g_file:
		wr = csv.writer(g_file, quoting=csv.QUOTE_ALL)	
		row =['product_type', 'Seller SKU', 'Brand', 'Product ID', 'Product ID Type',
			'Item Name', 'Manufacturer', 'Manufacturer Part Number', 'Recommended Browse Nodes', 
			'model', 'Color Map', 'Size', 'Included Components', 
			'Enclosure Material', 'Is Assembly Required', 'Item Type Name', 'Manufacturer Contact',
			'Item Heigh', 'Item Length', 'Item Width', 'unit Count', 'Item dimensions Unit of Measure',
			'Unit Count Type', 'Country Of Origin', 'Standard Price', 'Quantity', 'Maximum Retail Price',
			'Main Image URL',
			
			## Images
			'Other Image URL1', 'Other Image URL2', 'Other Image URL3', 'Other Image URL4',
			'Other Image URL5', 'Other Image URL6', 'Other Image URL7', 'Other Image URL8',
			'Swatch Image URL', 
			
			## Variation
			'Relationship Type', 'Variation Theme', 'Parent SKU', 'Parentage',
			  
			## Basic
			'Update Delete', 'Manufacturer', 'Description', 'Product Care Instructions',

			## Discovery
			'Search Terms', 'Bullet Point1', 'Bullet Point2', 'Bullet Point3',
			'Bullet Point4', 'Bullet Point5', 'color Name',	'Occassion', 'Finish', 
			'Pattern', 
			'Product Features1', 'Product Features2', 'Product Features3',
			'Product Features4', 'Product Features5', 'Style', 'Scent', 'Power Source',
			'Packer', 'Target Audience', 'lemght_range', 'Importer', 'Frame Type',
			'Theme', 'Department',
						
			## Diamesions
			'Shipping Weight',
			'Website Shipping Weight Unit of Measure', 'Shape', 'Item Volume', 'Item Volume Unit of Measure',
			'item Weight', 'Item Weight Unit of Measure', 'Display Volume', 'Item Display Width Unit of Measure',
			'Display Weight', 'Item Display Weight Unit of Measure', 'Display Width', 'Item Height Unit of Measure',
			'Display Depth', 'Item Display Depth Unit of Measure', 'Item Height', 
			'Item Display diameter', 'Size Map', 'Width Range', 'Item Display Diameter Unit of Measure',
			'Item Display Depth of Measure', 'Display Length', 'Display Length Unit of Measure',
			'Outside Diameter Delivered', 'Item Diameter Unit of Measure',
			

			#Compliance
			'Batteries are Included', 'Battary Type/Size 1', 'Battary Type/Size 2', 
			'Number of Batteries 1',  'Number of Battaries 2', 
			'Number of Batteries 3', 'Warranty Description', 'Safety Warning', 'Legal Disclaimer',
			'Is This Product a Battery or uses Battery?', 'Battery Comosition', 
			'Number of Lithium Metal Cells', 'Lithium Battery Packaging', 
			'Watt Hours per Battery', 'Lithium Battery Energy Content Unit of Measure',
			'Lithium Content', 'Lithium Battery Content', 'Lithium Battery Weigth Unit of Measure', 
			'Specific Uses of Product', 'HSN Code', 

			## Offer
			'Handling Time', 'Item Condition', 'Offer Condition Note', 'Launch Date', 'Release Date',
			'Number of Items', 'Item Package Quantity', 'Sale Start Date', 'Sale End Date', 
			'Sale Price', 'Restock Date', 'Is Giftwrap Avaiable?', 'Can Gift be Messaged?',
			'Is Discontinued by Manufacturer', 'Product Tax Code', 'Max Order Quantity', 
			'Offer End Date', 'Shipping-Template', 'Offer Start Date',

			##B2B
			'Business Price', 'Quantity Price Type', 'Quantity Price 1', 'Quantity Lower Bound 1',
			'Quantity Price 2', 'Quantity Lower Bound 2', 'Quantity Price 3', 'Quantity Lower Bound 3',
			'Quantity Price 4', 'Quantity Lower Bound 4', 'Quantity Price 5', 'Quantity Lower Bound 5',
			'Pricing Action'

			]
		wr.writerow(row)
		gallery = Gallery.objects.all().order_by('gallery_id')
		for g in gallery:	
			# Generate Amazon SKU Number
			sku_int = sku_int + 1
			amz_sku = sku_suf + str(sku_int)
			# END: Generate Amazon SKU Number	
			psku = amz_sku
			
			print("processing..." + str(g.gallery_id) )
			prod_name = "Styled Gallery Wall | A Set of Wall Art Paintings," + " Title: " + g.title
			prod_details = "Designer curated gallery wall. Set of " + str(g.set_of) + " art prints."
			incl_components = str(g.set_of) + " piece set of wall art."

			bullet1 = "Set your interiors a calls apart with our sesigner curated, well styled gallery wall set for wall decor."
			bullet2 = "Top notch quality. All materials sourced from the best in the industry"
			bullet3 = "Specifications=> Paper(when printed on paper): NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n Canvas(when printed on canvas): NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \nFrame: Made of polystyrene, which has classy finish, is highly durable, strong and light weight."

			###########################################
			## CREATE PARENT RECORD ########
			###########################################
			parentage = 'Parent'
			col_map = 'Multi-coloured'
			p_size = 'Size: ' + str(10) + '" X ' + str(10) + '" (inches)'
			t_size_width = 14
			t_size_height = 14
			parent_amz_sku = size_map = search_terms = color_name = col = variation = ''
			occassion = finish_type = pattern_name = ''
			style_name = 'Painting Set'
			scent_name = power_source_type = packer_contact_information = ''
			target_audience_base = length_range = importer_contact_information =''
			frame_type = theme = department = ''
			ship_weight = '1.5'
			item_volume = item_display_weight = display_volume = ''	
			size_map = 	'Medium'
			
			update_delete = 'update'
			qty = '1'
			item_total = 0.1
			item_total_mrp = 0.1
			row =['furnitureanddecor', psku, "ARTE'VENUE", 
					'', '', prod_name, 'Montage Art Pvt Ltd', "G-" + str(g.gallery_id), 
					'3749951031', "G-" + str(g.gallery_id),
					col_map, p_size, incl_components, 'Others',
					'Framed Wall Art Set for Home Decor', 'false', 'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',
					str(formatNumber(t_size_height)), str(formatNumber(t_size_width)), 2,
					1, 'inches', 'Unit', 'India', item_total, qty, item_total_mrp, g.room_view_url,				
					##Images
					'', '', '', '', '',
					'', '', '', '',
					
					## Variation
					variation, 'Size', parent_amz_sku, parentage,  
					
					## Basic Info
					update_delete, prod_details, "Wipe with soft, clean and dry cloti. No special care required.",
					
					## Discovery
					search_terms, 
					'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
					bullet1, bullet2, bullet3, 
					'Custom made for you. Comes with hooks and is ready to be hung on the wall.', 
					color_name, occassion, finish_type, pattern_name, 					
					"", "", "", "", "", 
					style_name, scent_name, power_source_type, packer_contact_information,
					target_audience_base, length_range, importer_contact_information,
					frame_type, theme, department,
					
					## - Diamensions
					ship_weight, 'KG', 'Square/Rectangular', item_volume, '', 
					ship_weight, 'KG', display_volume, '', item_display_weight, 'KG', 
					str(t_size_width + 3), 'IN', 8, 'IN', str(t_size_height + 3), '', size_map, '', '', 'IN', 
					8, 'IN', '', '',

					##-- Compliance
					'FALSE', "", "", "", "", "", "", 'Carries no warranties', '', 
					'Customized product. Return/Refund in case of damaged product delivery. The colors seen and product sizes specificed may change slightly.',
					'FALSE', '', '', '', '',  '', '', '', '',
					'Wall Decor', '',
					
					##-- Offer
					'2', 'New', '', '', '', '1', '1' ,'2020-12-01' ,'2021-06-30' , item_total, '', 'FALSE','',
					 '', '', '', '', '', '', '', 
					
					##-- B2B
					'', '', '', '', '', '', '', '' , '', '',
					'', '', ''

					#"", "", str(breadth*2.65), "CM", str(length*2.65), "CM", str(4*2.65), "CM" , str(itm_weight), "KG",
					
				]				
			wr.writerow(row)
			

			gw_variation = Gallery_variation.objects.filter(gallery = g).order_by('id')
			for gv in gw_variation:
				# Generate Amazon SKU Number
				sku_int = sku_int + 1
				amz_sku = sku_suf + str(sku_int)
				# END: Generate Amazon SKU Number

				gvsize = "Area covered on wall :" + str(gv.wall_area_width) + " X " + str(gv.wall_area_height) + " inches"
				
				items = Gallery_item.objects.filter(gallery_id = gv.gallery_id,
					gallery_variation_id = gv.id).order_by('item_id')

				gv_price = 0
				iprice = 0
				for i in items:
					iprice = get_variation_item_price(i.item_id)
					gv_price = gv_price + iprice 
					
				gv_price = round(gv_price + (gv_price * 20/100))
				
				cnt = 0
				item_details = 'The size mentioned is the approximate size it covers on the wall, including the gap between the artworks. \nTHIS SET INCLUDES: '
				for i in items:
					cnt = cnt + 1
					prod = Product_view.objects.filter(product_id = i.product_id, 
						product_type_id = 'STOCK-IMAGE').first()					
					breadth = formatNumber(i.image_width) 
					length = formatNumber(i.image_height) 
					if prod:	
						item_details = item_details + "\nPRODUCT #" + str(cnt) + " => Title: " + prod.name + " | "
					if i.moulding:
						if i.moulding.width_inner_inches:
							length = formatNumber(length + (i.moulding.width_inner_inches * 2))
						if i.mount:
							if i.mount_size:
								length = formatNumber(length + (i.mount_size * 2))
					
					breadth = formatNumber(i.image_width)
					if i.moulding:
						if i.moulding.width_inner_inches:
							breadth = formatNumber(breadth + (i.moulding.width_inner_inches * 2))
						if i.mount:
							if i.mount_size:
								breadth = formatNumber(breadth + (i.mount_size * 2))

					item_details = item_details + " Printed on " + i.print_medium_id.title() + ", print size: " + str(formatNumber(i.image_width)) + " X " + str(formatNumber(i.image_height)) + " inch.\n"
					if i.moulding_id:
						item_details = item_details + "Frame: " + i.moulding.name + " (" + str(formatNumber(i.moulding.width_inches)) + " inch).\n"
					if i.mount_id:
						item_details = item_details + "Mount: " + str(formatNumber(i.mount_size)) + " inch, Color: " + i.mount.name.lower() + ".\n"
					## Total Size
					t_size_width = i.image_width
					t_size_height = i.image_height
					if i.moulding:
						if i.moulding.width_inner_inches:
							t_size_width = t_size_width + i.moulding.width_inner_inches *2
							t_size_height = t_size_height + i.moulding.width_inner_inches *2
					if i.mount:
						t_size_width = t_size_width + i.mount_size*2
						t_size_height = t_size_height + i.mount_size*2
					
					t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
					item_details = item_details + "Product Size (with frame): " + t_size + "."
					if i.print_medium_id == "PAPER":
						if i.acrylic_id:
							item_details = item_details + "\nThe artwork is covered with clear acrylic on top."

				prod_details = "A set of " + str(g.set_of) + " art prints. \n" + item_details
				search_terms = (" painting set, wall art set, wall art panels, paintings, wall paintings, wall art, wall decor, paintings for home decor, art print, paintings with frame, paintings for living room, paintings for bed room, wall decor ")[:150]
				
				parentage = 'Child'
				variation = 'Variation'
				col = 'Multi'
				col_map = 'Multi-coloured'
				##p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Print on ' + i.print_medium_id.title()
				size_map = 'Medium'
				qty = '1000'
				parent_amz_sku = psku
				
				gv_total_mrp = round(gv_price + (gv_price * 20 /100))
				
				prod_name =  "Styled Gallery Wall | A Set of Wall Art Paintings," + " Title: " + g.title

				update_delete = "Update"
				if i.gallery.is_published == False:
					update_delete = "Delete"


				## Create variation records
				color_name = ''
				occassion = ''
				finish_type = 'Matt finish'
				pattern_name = ''
				style_name = 'A Set of Paintings'
				scent_name = ''
				power_source_type = ''
				packer_contact_information = ''
				target_audience_base = ''
				length_range = ''
				importer_contact_information = ''
				frame_type = 'Hanging'
				theme = ''
				department = ''
				item_volume = ''
				display_volume = ''
				
				t_size = t_size_width * t_size_height
				if t_size <= 256:
					ship_weight = 1.5 * g.set_of
				elif t_size <= 576:
					ship_weight = 2  * g.set_of
				elif t_size <= 900:
					ship_weight = 2.5  * g.set_of
				elif t_size <= 1600:
					ship_weight = 3  * g.set_of
				else:
					ship_weight = 3.5  * g.set_of
		
				item_display_weight = ship_weight
				
				model_number = 'G-' + str(g.gallery_id) + ':' + str(gv.id)
				row =['furnitureanddecor', amz_sku, "ARTE'VENUE", 
					'', '', prod_name, 'Montage Art Pvt Ltd', model_number, '3749951031', 
					model_number,
					col_map, gvsize, incl_components, 'Others',
					'Framed Wall Art for Home Decor', 'false', 
					'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',
					str(formatNumber(t_size_height)), str(formatNumber(t_size_width)), 2,
					1, 'inches', 'Unit', 'India', gv_price, qty, 
					gv_total_mrp, g.room_view_url,
					
					##Images
					'', '', '', '', '',
					'', '', '', '',
					
					## Variation
					variation, 'Size', parent_amz_sku, parentage,  
					
					## Basic Info
					update_delete, prod_details, "Wipe with soft, clean and dry cloti. No special care required.",
					
					## Discovery
					search_terms, 
					'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
					bullet1, bullet2, bullet3, 
					'Custom made for you. Comes with hooks and is ready to be hung on the wall.', 
					color_name, occassion, finish_type, pattern_name, 					
					"", "", "", "", "", 
					style_name, scent_name, power_source_type, packer_contact_information,
					target_audience_base, length_range, importer_contact_information,
					frame_type, theme, department,
					
					## - Diamensions
					ship_weight, 'KG', 'Square/Rectangular', item_volume, '', 
					ship_weight, 'KG', display_volume, '', item_display_weight, 'KG', 
					str(t_size_width + 3), 'IN', 8, 'IN', str(t_size_height + 3), '', size_map, '', '', 'IN', 
					8, 'IN', '', '',

					##-- Compliance
					'FALSE', "", "", "", "", "", "", 'Carries no warranties', '', 
					'Customized product. Return/Refund in case of damaged product delivery. The colors seen and product sizes specificed may change slightly.',
					'FALSE', '', '', '', '',  '', '', '', '',
					'Wall Decor', '',
					
					##-- Offer
					'2', 'New', '', '', '', '1', '1' ,'2020-12-01' ,'2021-06-30' , gv_price, '', 'FALSE','',
					 '', '', '', '', '', '', '', 
					
					##-- B2B
					'', '', '', '', '', '', '', '' , '', '',
					'', '', ''

					#"", "", str(breadth*2.65), "CM", str(length*2.65), "CM", str(4*2.65), "CM" , str(itm_weight), "KG",
					
				]
				
				wr.writerow(row)

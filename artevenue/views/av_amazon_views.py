from artevenue.models import Product_view, Moulding, Moulding_image
from artevenue.models import Curated_collection, Mount
from artevenue.models import Amazon_data, Stock_image_stock_image_category
from gallerywalls.models import Gallery, Gallery_variation, Gallery_item
from django.conf import settings
from django.http import HttpRequest
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

from django.conf import settings

env = settings.EXEC_ENV
if env == 'PROD':
	cfile = '/home/artevenue/website/estore/static/feeds/non_gallery_creatives.csv'
	sku_seq = '/home/artevenue/website/estore/static/feeds/sku_seq.csv'
else:
	cfile = 'c:/artevenue/PRODUCT_FEEDS/non_gallery_creatives.csv'
	sku_seq = 'c:/artevenue/PRODUCT_FEEDS/sku_seq.csv'


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



def create_images_by_prod_ids(ids, product_type_id, amz_sku, image_width, image_height, moulding_id, mount_color, mount_size, parent_child, print_medium_id, stretch_id):

	amazon_data = Stock_image.objects.filter(product_id__in = ids)
	
	for h in amazon_data:
			

		#if moulding_id:
			#framed_img = get_amz_FramedImage_api(h.product_id, moulding_id, 
			#	mount_color, mount_size, int(image_width))

		if not mount_size:
			mount_size = 0
			
		if not moulding_id:
			moulding_id = ''
		if not mount_color:
			mount_color = ''			
			
		stretched_canvas = 'NO'
		if print_medium_id == 'CANVAS' and (moulding_id == None or moulding_id == '' or moulding_id == '0') and stretch_id == '1':
			stretched_canvas = 'YES'
			
		from django.http import HttpRequest
		request = HttpRequest()
		request.GET['prod_id'] = h.product_id
		request.GET['moulding_id'] = moulding_id
		request.GET['mount_color'] = mount_color
		request.GET['mount_size'] = mount_size
		request.GET['prod_type'] = product_type_id
		request.GET['stretched_canvas'] = stretch_id
		request.GET['imgtilt'] = 'YES'
		request.GET['dropshadow'] = 'NO'
		
		
		framed_img = get_FramedImage_by_id(request, h.product_id, moulding_id, mount_color=mount_color, 
							mount_size=float(mount_size), user_width=float(image_width), prod_type=h.product_type_id, 
							stretched_canvas=stretched_canvas, imgtilt='YES', dropshadow='NO' )
						
		aspect_ratio = framed_img.width / framed_img.height
		framed_img = framed_img.resize( (1200, int(round(1200/aspect_ratio))) )				
								
			
		f_nm = "f_"
		#else:
		#	framed_img = get_amz_FramedImage_api(h.product_id)
		#	f_nm = "n_"
			
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
		lowres_img_name = amz_sku +"_" + h.url[loc:]
		
		# save image
		#ifile = Path(img_loc + lowres_img_name)
		#if ifile.is_file():
		#	print("Image already available...skipping - Main image")
		#else:
		framed_img.save(img_loc + lowres_img_name)
		
		## Generate card images only for child rows
		if parent_child == 'C':
			if moulding_id :
				m_id = moulding_id
				if mount_color:
					mnt_color = mount_color
					mnt_size = float(mount_size)
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
			request.GET['image_width'] = image_width
			request.GET['prod_type'] = product_type_id

			## Card 1
			request.GET['card_no'] = '2'
			card = get_catalog_card(request, False)
			low_res_card1 = amz_sku +"_card1_" + h.url[loc:]
			# save image
			c1file = Path(img_loc + low_res_card1)
			#if c1file.is_file():
			#	print("Image already available...skipping - Card 1")
			#else:
			card.save(img_loc + low_res_card1)
			
			
		print("Saved: " + lowres_img_name)	


def NEW_amz_data():
	cnt = 0
	sku_suf = "AV-"
	sku_int = 194135

	## Collect all prod ids for non-gallery products with creatives
	non_g_prods = []
	with open(cfile) as nfile:
		non_g = csv.reader(nfile, delimiter=',')
		for n in non_g:
			non_g_prods.append(n[0])
	
	## Exclude already created
	excl_ids = Amazon_data.objects.distinct().values('product_id')		
	
	## All curated products
	curated = Curated_collection.objects.exclude(product_id__in = excl_ids)		
	
	print("processing..." + str(curated.count()))
	cnt = 0

	for c in curated:
		prod = c.product
		## Skip non-gallery prods that have creative
		if prod.product_id in non_g_prods:
			print("skipping " + str(prod.product_id))
			continue
		
		if prod.is_published == False:
			print("skipping " + str(prod.product_id) + ", it is not published.")
			continue				
		
		cnt = cnt + 1
		print(str(cnt) + "...")


		## Check if this product is already processed
		'''
		p = Amazon_data.objects.filter(product_id = prod.product_id).first()
		if p:
			print( "Product = " + str(prod.product_id)  + " is already processed, skipping")
			continue
		'''
		
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
			image_height = (16 / prod.aspect_ratio),
			created_date = today,
			updated_date = today,
			parent_child = 'P',
			parent_amz_sku = ''
		)
		hl.save()


		#########################################################
		## Create versions with different sizes
		#########################################################
		if prod.aspect_ratio > 1:
			h = 10
			w = round(h * prod.aspect_ratio)
			STANDARD_PROD_WIDTHS = [w, w+4 , w+8, w+12, w+16, w+20]
		else:
			STANDARD_PROD_WIDTHS = [10, 14, 18, 22, 26, 30]

		if prod.artist == 'Huynh, Duy':
			if prod.aspect_ratio > 1:
				h = 16
				w = round(h * prod.aspect_ratio)
				STANDARD_PROD_WIDTHS = [w, w+4 , w+8, w+14, w+20]
			else:
				STANDARD_PROD_WIDTHS = [16, 20, 24, 30, 36]


		for size in STANDARD_PROD_WIDTHS:		
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

	with open(sku_seq, 'w', newline='') as sku_file:
		wr_sku = csv.writer(sku_file, quoting=csv.QUOTE_ALL)
		row_sku =['AV-', sku_int]
		wr_sku.writerow(row_sku)


	print("Data creation/Update complete: Count - " + str(cnt) )


def NEW_create_amz_images(amz_key_from=209724, amz_key_to=215730, ids=None):

	##Done: 196722 - 197722
	##Done: 197723 - 198723
	##Done: 199723 - 199723
	##Done: 199724 - 201723
	##Done: 201724 - 202723
	##Done: 202724 - 205723
	##Done: 205724 - 209723
	

	amazon_data = Amazon_data.objects.filter(is_published = True,
		amazon_key__gte = amz_key_from, 
		amazon_key__lte = amz_key_to
		).order_by('product_id')
	
	if ids:
		amazon_data = amazon_data.filter(product_id__in = ids)

	## Collect all prod ids for non-gallery products with creatives
	if env == 'PROD':
		cfile = '/home/artevenue/website/estore/static/feeds/non_gallery_creatives.csv'	
	else:
		cfile = 'c:/artevenue/PRODUCT_FEEDS/non_gallery_creatives.csv'

	## Collect all prod ids for non-gallery products with creatives
	non_g_prods = []
	with open(cfile) as nfile:
		non_g = csv.reader(nfile, delimiter=',')
		
		for n in non_g:
			non_g_prods.append(n[0])
			
	with open(cfile) as ngal_file:
		non_gallery = csv.reader(ngal_file, delimiter=',')		
		
		for h in amazon_data:
			print("Processing: " + str(h.amazon_sku))
							
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

				## If this prod has a creative, then framed image is the crative
				if h.product_id in non_g_prods:
					for n in non_gallery:
						if n[0] == p.product_id:
							framed_url = n[1]
							card1_url = img_url + lowres_img_name
				else:
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
				
					framed_url = img_url + lowres_img_name
					card1_url = img_url + low_res_card1
				
			if h.parent_child == 'C':
				## Save in urls table
				hf = Amazon_data.objects.filter(amazon_key = h.amazon_key).update(	
						framed_url = framed_url,
						card1_url = card1_url, 
						card2_url = 'https://www.artevenue.com/static/img/catalog/amz_f_card.jpg'
						) 
			else:
				## Save in urls table
				hf = Amazon_data.objects.filter(amazon_key = h.amazon_key).update(	
						framed_url = img_url + lowres_img_name)			
				
			print("Saved: " + lowres_img_name)


def NEW_createAmzFile(amz_key_from=196722, amz_key_to=215730, ids=None):
	##Done: 196722 - 197722
	##Done: 197723 - 198723
	##Done: 199723 - 199723
	##Done: 199724 - 201723
	##Done: 201724 - 202723
	##Done: 202724 - 205723
	##Done: 205724 - 209723
	
	amz = Amazon_data.objects.filter(is_published = True,
		amazon_key__gte = amz_key_from, 
		amazon_key__lte = amz_key_to
		).order_by('product_id')
	
	if ids:
		amazon_data = amazon_data.filter(product_id__in = ids)
	
	print("COUNT: " + str(amz.count()) )
		
	file_nm = 'av_amz_data_' + str(amz_key_from) + '_to_' + str(amz_key_to) + '.csv'
	
	with open(file_nm, 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row =['product_type', 'Seller SKU', 'Brand', 'Product ID', 'Product ID Type',
			'Product Description', 
			'Item Name', 'Recommended Browse Nodes', 'Country Of Origin', 'HSN Code',
			'Maximum Retail Price', 'Main Image URL', 'Quantity', 'Standard Price', 
			
			## Images
			'Other Image URL1', 'Other Image URL2', 'Other Image URL3', 'Other Image URL4',
			'Other Image URL5', 'Other Image URL6', 'Other Image URL7', 'Other Image URL8',
			'Swatch Image URL', 

			## Variation
			'Relationship Type', 'Variation Theme', 'Parent SKU', 'Parentage',

			## Basic
			'Update Delete', 'Manufacturer Part Number', 'Manufacturer', 
			'Product Exemption Reason'

			## Discovery
			'Bullet Point1', 'Bullet Point2', 'Bullet Point3',
			'Bullet Point4', 'Bullet Point5', 'Frame Type', 'Search Terms', 
			'color Name', 'Packer', 'Item Type Name', 'Theme', 'Size', 'Color Map', 
			'Frame Material Type', 'Paint Type', 'Importer', 'Material Type',
			'Manufacturer Contact',
			
			## Dimensions
			'Item Width Unit of Measure', 'Item Height Unit of Measure', 'Item Width', 
			'Item Height', 'Size Map', 'Shape', 'Item Length Unit of Measure', 
			'Item Length', 'Unit Count Type', 'Unit Count',
			
			## Fulfilment
			'Package Height Unit of Measure', 'Package Length', 'Package Width',
			'Package Weight Unit of Measure', 'Package Height', 
			'Package Width Unit of Measure', 'Fulfilment Center ID',
			'Package Length Unit of Measure', 'Package Weight',
			
			#Compliance
			'Is This Product a Battery or uses Battery?', 
			'Batteries are Included', 'Battery Comosition',
			'Battery Type/Size 1', 'Battery Type/Size 2', 'Battery Type/Size 3', 
			'Number of Batteries 1',  'Number of Battaries 2', 'Number of Batteries 3', 
			'Battery Weight', 'Battery Weight Unit of Measure', 
			'Number of Lithium Metal Cells', 'Number of Lithium Ion Cells',
			'Lithium Battery Packaging', 'Watt Hours per Battery', 
			'Lithium Battery Energy Content Unit of Measure', 'Lithium content',
			'Lithium Battery Weigth Unit of Measure', 
			'Applicable Dangerous Goods Regulations1',
			'Applicable Dangerous Goods Regulations2',
			'Applicable Dangerous Goods Regulations3',
			'Applicable Dangerous Goods Regulations4',
			'Applicable Dangerous Goods Regulations5',
			#'UN Number', 'Safty Data Sheet URL', 			
			#'item Weight', 'Item Weight Unit of Measure', 
			#'Item Volume', 'Item Volume Unit of Measure',
			#'Flash Point (C)', 'Categorisation/GHS Pictogram1', 
			#'Categorisation/GHS Pictogram2',  'Categorisation/GHS Pictogram3', 
			
			## Offer
			'Is Giftwrap Avaiable?', 'Minimum Advertized Price', 'List Price',
			'Release Date', 'Offer End Date', 'Currency', 'Max Order Quantity',
			'Merchant Shipping Group Name',  'Offer Start Date', 'Restock Date',
			'Product Tax Code', 'Handling Time', 'Can Gift be Messaged?',
			'Condition', 'Condition Note', 'Sale Price', 
			'Sale Start Date', 'Sale End Date', 

			##B2B
			'Business Price', 'Quantity Price Type', 'Quantity Price 1', 
			'Quantity Lower Bound 1', 'Quantity Price 2', 
			'Quantity Lower Bound 2', 'Quantity Price 3', 'Quantity Lower Bound 3',
			'Quantity Price 4', 'Quantity Lower Bound 4', 'Quantity Price 5', 
			'Quantity Lower Bound 5', 'Pricing Action', 
			'United Nations Stadard Products and Service Code', 'National Stock Number'

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
				col_map = 'Multi'
				p_size = 'Size: ' + str(10) + '" X ' + str(10) + '" (inches)'
				size_map = ''
				qty = '1'
				item_total = 0
				parent_amz_sku = ''
				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"
			else:
				parentage = 'Child'
				variation = 'Variation'
				col = ''
				col_map = 'Multi'
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Print on ' + h.print_medium_id.title()
				size_map = 'Medium'
				qty = '1000'
				item_total = h.item_total
				parent_amz_sku = h.parent_amz_sku
				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"
			
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
			packer_contact_name = ''
			target_audience_base = ''
			length_range = ''
			importer_contact_information = ''
			frame_type = 'Framed'
			theme = cat
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
				
			row =['wallart', h.amazon_sku, "ARTE'VENUE", 
				'', '', prod_details, prod_name, '3749951031', 
				'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
				h.framed_url, qty, 
				item_total if item_total > 0 else 0.01, 
				
				##Images
				h.card1_url, h.card2_url, h.card3_url, h.card4_url, h.card5_url,
				'', '', '', '',
				
				## Variation
				variation, 'Size', parent_amz_sku, parentage,  
					
				## Basic Info
				update_delete, h.part_number, 'Montage Art Pvt Ltd', 
				'',
				
				## Discovery
				bullet1, bullet2, bullet3, 
				'Comes with hooks and is ready to be hung on the wall.', 
				'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
				frame_type, search_terms, color_name, packer_contact_information,
				'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
				h.print_medium_id.title(), 
				'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',

				## - Diamensions
				'IN', 'IN', t_size_width, t_size_height, size_map, sq_re,
				'IN', 2, 'Count', 1,

				## Fulfilment
				'IN', 3, str(t_size_width + 3),
				'KG', str(t_size_height + 3), 'IN', '', 'IN', 
				ship_weight, 
				
				##-- Compliance
				'FALSE', '', '',  
				'', '', '', '', '', '', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '',

				##-- Offer
				'FALSE', 
				item_total if item_total > 0 else 0.01, item_total_mrp if item_total_mrp > 0 else 0.01,
				'', '12-31-2022',  'INR', 100, '', 
				'03/23/2021', '', 'A_GEN_REDUCED',
				'2', 'FALSE', 'New', '', item_total if item_total > 0 else 0.01, 
				'03/23/2021', '12/31/2022',
				
				##-- B2B
				'', '', '', '', '', '', '', ''
				]
				
			wr.writerow(row)



def creative_prod_data():
	amz_sku = 'AV-C-'
	sku_int = 0
	if env == 'PROD':
		f_input = '/home/artevenue/website/estore/static/feeds/amazon/creative_prods_data.csv'
		sku_seq = '/home/artevenue/website/estore/static/feeds/amazon/sku_seq.csv'
		amz_feed = '/home/artevenue/website/estore/static/feeds/amazon/amz_prods_data.csv'
		creative_url = 'https://artevenue.com/static/feeds/amazon/creatives/'
	else:
		f_input = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/CREATIVE_PRODS/creative_prods_data.csv'
		sku_seq = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/CREATIVE_PRODS/sku_seq.csv'
		amz_feed = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/CREATIVE_PRODS/amz_prods_data.csv'
		creative_url = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/CREATIVE_PRODS/'

	cfile = Path(f_input)
	if not cfile.is_file():
		print("creative_prods_data.csv file did not found")
		return

	file = open(cfile)	
	cr = csv.reader(file, delimiter=',')
	
	with open(amz_feed, 'w', newline='') as amz_out:
		wr = csv.writer(amz_out, quoting=csv.QUOTE_ALL)
		cnt = 0
		for row in cr:
			cnt = cnt+1
			if cnt <= 2:
				continue
				
			product_id = row[0]
			product_type_id = row[12]
			if not product_id:
				print("Product id not found, skipped...")
				continue
			
			p = Stock_image.objects.filter(product_id = product_id).first()				
			if not p:
				print("Product " + product_id + " not found, skipped...")
				continue
				
			if p.is_published == False:
				print("Product " + product_id + " not found, skipped...")
				continue

			print("processing..." + str(product_id) )
			
				
			image_width = row[4]
			image_height = row[5]
			
			mld_id = row[8]
			mnt_id = row[9]
			mnt_size = row[10] if row[10] else '0'
			acr_id = row[6]
			brd_id = row[7]
			str_id = row[13]				
			print_medium_id = row[11]
			
			if mld_id:
				moulding = Moulding.objects.filter(moulding_id = int(mld_id)).first()
			else: 
				moulding = None
			if mnt_id:
				mount = Mount.objects.filter(mount_id = int(mnt_id)).first()
				mnt_color = mount.color
			else:
				mount = None
				mnt_color = ''
			
			## Get product category
			cate = Stock_image_stock_image_category.objects.filter(
				stock_image = p).first()
			cat = cate.stock_image_category.name.title()
			
			#  Get Price
			#  Get the item price
			price = get_prod_price(product_id, 
					prod_type= product_type_id,
					image_width=image_width, 
					image_height=image_height,
					print_medium_id = print_medium_id,
					acrylic_id = acr_id,
					moulding_id = mld_id,
					mount_size = mnt_size,
					mount_id = mnt_id,
					board_id = brd_id,
					stretch_id = str_id)
			item_total = price['item_price']
			msg = price['msg']
			cash_disc = price['cash_disc']
			percent_disc = price['percent_disc']
			item_unit_price = price['item_unit_price']
			item_disc_amt = price['disc_amt']
			disc_applied = price['disc_applied']
			promotion_id = price['promotion_id']
			# END::::    Get the item price
		
			# 	if item price not found, return
			if item_total == 0 or item_total is None:				
				err_flg = True
				print( 'Price not available for this image ' + str(p.product_id) )
				continue
			# END:	if item price not found, don't add to cart

			## Increase price by 20%, to manage the returns			##################################################
			item_total = item_total + round((item_total*20/100))


			#	Calculate sub total, tax for the item
			item_tax = 0
			item_sub_total = 0
			#### Get Tax
			taxes = get_taxes()
			if product_type_id == 'STOCK-IMAGE':
				tax_rate = taxes['stock_image_tax_rate']
			if product_type_id == 'ORIGINAL-ART':
				tax_rate = taxes['original_art_tax_rate']
			if product_type_id == 'USER-IMAGE':
				tax_rate = taxes['user_image_tax_rate']
			if product_type_id == 'STOCK-COLLAGE':
				tax_rate = taxes['stock_image_tax_rate']
			if product_type_id == 'FRAME':
				tax_rate = taxes['frame_tax_rate']	
			
			quantity = 1
			
			# Calculate tax and sub_total
			item_sub_total = round( (item_total*quantity) / (1 + (tax_rate/100)), 2 )
			item_tax = round( (item_total*quantity) - item_sub_total )

			item_total_mrp = round(item_total + (item_total * 20 /100))	

			length = int(image_height)
			if moulding:
				if moulding.width_inner_inches:
					length = length + (moulding.width_inner_inches * 2)
				if mount:
					if mnt_size:
						length = length + (int(mnt_size) * 2)
			
			breadth = int(image_width)
			if moulding:
				if moulding.width_inner_inches:
					breadth = breadth + (moulding.width_inner_inches * 2)
				if mount:
					if mnt_size:
						breadth = breadth + (int(mnt_size) * 2)			

			prod_details = cat + " painting with frame, Title: " + p.name + ", Artist: " + p.artist + ".\nPrinted on: " + print_medium_id.title() + "; Framed Art Print. "
			prod_details = prod_details + "Print Size: " + str(image_width) + " X " + str(image_height) + "; \n"
			incl_components = "One piece " + cat + " art with frame, printed on " + print_medium_id.title() + "; "
			incl_components = incl_components + "Print Size: " + str(image_width) + " X " + str(image_height) + "; "
			
			if print_medium_id.upper() == 'PAPER':
				if moulding:
					bullet1 = 'Printed on ' + print_medium_id.title() + ', size: ' + str(int(image_width) + (moulding.width_inner_inches *2) + (int(mnt_size) *2) ) + " X " + str(int(image_height) + (moulding.width_inner_inches * 2) + ( int(mnt_size) * 2) ) + " inch. "
				else:
					bullet1 = "Printed on " + print_medium_id.title() + ", size: " + str(image_width) + " X " + str(image_height) + " inch. "
				prod_details = prod_details + "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
			else:
				if moulding:
					bullet1 = 'Printed on ' + print_medium_id.title() + ', size: ' + str(int(image_width) + (moulding.width_inner_inches *2) ) + " X " + str(int(image_height) + (moulding.width_inner_inches * 2) ) + " inch. "
				else:
					bullet1 = "Printed on " + print_medium_id.title() + ", size: " + str(image_width) + " X " + str(image_height) + " inch. "
				prod_details = prod_details + "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \n"
			bullet2 = ''
			t_size = ''
			if moulding:
				prod_details = prod_details + "Frame: " + moulding.name + " (" + str(moulding.width_inches) + " inch), made of polystyrene, light weight, long lasting and very good finish. \n"
				incl_components = incl_components + "Frame: " + moulding.name + " (" + str(moulding.width_inches) + " inch). "
				bullet2 = "Frame: " + moulding.name + " (" + str(moulding.width_inches) + " inch). It's a high quality frame made of Polystyrene, which is light weight, long lasting and has very good finish. \n" 
			if mount:
				prod_details = prod_details + "Mount: " + str(mnt_size) + " inch, Color: " + mount.name.lower() + ", it enhances the look of this artwork. \n"
				incl_components =  incl_components + "Mount: " + str(mnt_size) + " inch, Color: " + mount.name.lower() + ". "
				bullet2 = bullet2 + ", " +str(mnt_size) + " inch " + mount.name.lower() + " mount adds classy look to this art. "
			## Total Size
			t_size_width = int(image_width)
			t_size_height = int(image_height)
			if moulding:
				if moulding.width_inner_inches:
					t_size_width = t_size_width + moulding.width_inner_inches *2
					t_size_height = t_size_height + moulding.width_inner_inches *2
			if mount:
				t_size_width = t_size_width + int(mnt_size)*2
				t_size_height = t_size_height + int(mnt_size)*2
			
			t_size = str(t_size_width) + " X " + str(t_size_height) + " inch "
			prod_details = prod_details + "Product Size (with frame): " + t_size
			incl_components = incl_components + "Product Size (with frame): " + t_size
			
			bullet3 = ''
			if print_medium_id.upper() == "PAPER":
				if acr_id:
					prod_details = prod_details + "\nThe artwork is covered with clear acrylic for added protection, durability and clear visibility. Acrylic is light weight and durable."
					incl_components = incl_components + "Acrylic covered; "
				bullet3 = "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility."
			else:
				bullet3 = "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions."
				

			search_terms = ( cat + " paintings, wall paintings, wall art, paintings for home decor, art print, paintings with frame, paintings for living room, paintings for bed room, wall decor " + p.key_words.replace('|', ', '))[:150]

			prod_name =  cat + " painting with frame, Title: " + p.name + "; Framed Art Print on "  + print_medium_id.title() + "; (" + t_size + ") | Arte'Venue"

			# Generate Amazon SKU Number
			sku_suf = 'AV-C-'

			update_delete = "Update"
			if Decimal(image_width) > p.max_width or Decimal(image_height) > p.max_height:
				update_delete = "Delete"
				
			######################################
			## If the current is a parent, then 
			## first create the parent row first 
			## and then the same as child
			######################################
			if row[15] == "P":
				## Create product image
				ids = [product_id]

				# Generate Amazon SKU Number
				sku_int = sku_int + 1
				amz_sku = sku_suf + str(sku_int)
				# END: Generate Amazon SKU Number

				create_images_by_prod_ids(ids, product_type_id, amz_sku, image_width, image_height, mld_id, mnt_color, int(mnt_size), 'P', print_medium_id, str_id)

				## Product Image location
				img_url = ''
				if env == 'DEV' or env == 'TESTING':
					img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "amazon_data/images/" 
					img_url = img_loc
				else:
					img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "amazon_data/images/"
					img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "amazon_data/images/"
				
				pos = p.url.rfind('/')
				loc = 0
				if pos > 0:
					loc = pos+1
				lowres_img_name = amz_sku +"_" + p.url[loc:]
				
				prod_img = (img_url + lowres_img_name)

				low_res_card1 = amz_sku +"_card1_" + p.url[loc:]
				card_1_img = (img_url + low_res_card1)


				parentage = 'Parent'
				variation = ''
				col = ''
				col_map = 'Multi'
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" inches, Printed on ' + print_medium_id.title()
				size_map = 'Medium'
				qty = '1000'
				item_total = item_total
				parent_amz_sku = ''
				color_name = ''
				occassion = ''
				finish_type = 'Matt finish'
				pattern_name = ''
				style_name = cat
				scent_name = ''
				power_source_type = ''
				packer_contact_information = ''
				packer_contact_name = ''
				target_audience_base = ''
				length_range = ''
				importer_contact_information = ''
				frame_type = 'Framed'
				theme = cat
				department = ''
				item_volume = ''
				display_volume = ''
				
				t_size = int(t_size_width) * int(t_size_height)
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
					

				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"

				
				## Create parent row
				row_p =['wallart', amz_sku, "ARTE'VENUE", 
					'', '', prod_details, prod_name, '3749951031', 
					'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
					creative_url + row[2], qty, 
					item_total if item_total > 0 else 0.01, 
					
					##Images
					prod_img, '', '', '', '', '', '', '', '',
					
					## Variation
					variation, 'Size', parent_amz_sku, parentage,  
						
					## Basic Info
					update_delete, p.part_number, 'Montage Art Pvt Ltd', 
					'',
					
					## Discovery
					bullet1, bullet2, bullet3, 
					'Comes with hooks and is ready to be hung on the wall.', 
					'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
					frame_type, search_terms, color_name, packer_contact_information,
					'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
					print_medium_id.title(), 
					'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',

					## - Diamensions
					'IN', 'IN', t_size_width, t_size_height, size_map, sq_re,
					'IN', 2, 'Count', 1,

					## Fulfilment
					'IN', 3, str(t_size_width + 3),
					'KG', str(t_size_height + 3), 'IN', '', 'IN', 
					ship_weight, 
					
					##-- Compliance
					'FALSE', '', '',  
					'', '', '', '', '', '', '', '', '', '',
					'', '', '', '', '', '', '', '', '', '',
					'', '', '', '', '', '', '', '', '', '',

					##-- Offer
					'FALSE', 
					item_total if item_total > 0 else 0.01, item_total_mrp if item_total_mrp > 0 else 0.01,
					'', '12-31-2022',  'INR', 100, '', 
					'03/23/2021', '', 'A_GEN_REDUCED',
					'2', 'FALSE', 'New', '', item_total if item_total > 0 else 0.01, 
					'03/23/2021', '12/31/2022',
					
					##-- B2B
					'', '', '', '', '', '', '', ''
					]
					
				wr.writerow(row_p)
				
				parent_amz_sku = amz_sku
			### END PARENT ROW


			######################################
			### Child Row starts
			######################################
				
			# Generate Amazon SKU Number for the child row
			sku_int = sku_int + 1
			amz_sku = sku_suf + str(sku_int)

			## Create product image
			ids = [product_id]
			create_images_by_prod_ids(ids, product_type_id, amz_sku, image_width, image_height, mld_id, mnt_color, int(mnt_size), 'C', print_medium_id, str_id)

			## Product Image location
			img_url = ''
			if env == 'DEV' or env == 'TESTING':
				img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "amazon_data/images/" 
				img_url = img_loc
			else:
				img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "amazon_data/images/"
				img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "amazon_data/images/"
			
			pos = p.url.rfind('/')
			loc = 0
			if pos > 0:
				loc = pos+1
			lowres_img_name = amz_sku +"_" + p.url[loc:]
			
			prod_img = (img_url + lowres_img_name)

			low_res_card1 = amz_sku +"_card1_" + p.url[loc:]
			card_1_img = (img_url + low_res_card1)

			parentage = 'Child'
			variation = 'Variation'
			col = ''
			col_map = 'Multi'
			p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" inches, Printed on ' + print_medium_id.title()
			size_map = 'Medium'
			qty = '1000'
			item_total = item_total
			parent_amz_sku = parent_amz_sku
			color_name = ''
			occassion = ''
			finish_type = 'Matt finish'
			pattern_name = ''
			style_name = cat
			scent_name = ''
			power_source_type = ''
			packer_contact_information = ''
			packer_contact_name = ''
			target_audience_base = ''
			length_range = ''
			importer_contact_information = ''
			frame_type = 'Framed'
			theme = cat
			department = ''
			item_volume = ''
			display_volume = ''
			
			t_size = int(t_size_width) * int(t_size_height)
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
				

			if t_size_width == t_size_height:
				sq_re = "Square"
			else:
				sq_re = "Rectangle"

			row_c =['wallart', amz_sku, "ARTE'VENUE", 
				'', '', prod_details, prod_name, '3749951031', 
				'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
				creative_url + row[2], qty, 
				item_total if item_total > 0 else 0.01, 
				
				##Images
				prod_img, card_1_img, '', '', '', '', '', '', '',
				
				## Variation
				variation, 'Size', parent_amz_sku, parentage,  
					
				## Basic Info
				update_delete, p.part_number, 'Montage Art Pvt Ltd', 
				'',
				
				## Discovery
				bullet1, bullet2, bullet3, 
				'Comes with hooks and is ready to be hung on the wall.', 
				'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
				frame_type, search_terms, color_name, packer_contact_information,
				'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
				print_medium_id.title(), 
				'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',

				## - Diamensions
				'IN', 'IN', t_size_width, t_size_height, size_map, sq_re,
				'IN', 2, 'Count', 1,

				## Fulfilment
				'IN', 3, str(t_size_width + 3),
				'KG', str(t_size_height + 3), 'IN', '', 'IN', 
				ship_weight, 

				
				##-- Compliance
				'FALSE', '', '',  
				'', '', '', '', '', '', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '',

				##-- Offer
				'FALSE', 
				item_total if item_total > 0 else 0.01, item_total_mrp if item_total_mrp > 0 else 0.01,
				'', '12-31-2022',  'INR', 100, '', 
				'03/23/2021', '', 'A_GEN_REDUCED',
				'2', 'FALSE', 'New', '', item_total if item_total > 0 else 0.01, 
				'03/23/2021', '12/31/2022',
				
				##-- B2B
				'', '', '', '', '', '', '', ''
				]
				
			wr.writerow(row_c)




def gallerywalls_data():
	sku_suf = 'AV-G-'
	sku_int = 562
	parent_amz_sku = ''
	
	
	if env == 'PROD':
		amz_feed = '/home/artevenue/website/estore/static/feeds/amazon/gallerywalls_data.csv'
		g_partnumber_sku = '/home/artevenue/website/estore/static/feeds/amazon/gallerywalls_partnumber_sku.csv'
	else:
		sku_seq = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/CREATIVE_PRODS/sku_seq.csv'
		amz_feed = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/CREATIVE_PRODS/gallerywalls_data.csv'
		g_partnumber_sku = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/UPLOADS/gallerywalls_partnumber_sku.csv'

	'''
	with open(g_partnumber_sku, mode='r') as skufile:
		sf = csv.reader(skufile)
		mydict = {rows[0]:rows[1] for rows in sf}	
	'''
	
	with open(amz_feed, 'w', newline='') as amz_out:
		wr = csv.writer(amz_out, quoting=csv.QUOTE_ALL)
		cnt = 0
		gallery = Gallery.objects.filter(is_published=True, set_of__lte = 8, gallery_id__gt = 132)

		for g in gallery:
			cnt = cnt+1

			### GET VARIATION
			gallery_variations = Gallery_variation.objects.filter(gallery_id = g.gallery_id).order_by('-is_parent') ## Order by is very important

			for gv in gallery_variations:

				print("Processing: " + str(g.gallery_id) + " - " + str(gv.id))
				gallery_items = Gallery_item.objects.filter(gallery_id = g.gallery_id, 
					gallery_variation = gv)
				'''
				gallery_items = gallery_items.values(
						'item_id', 'gallery_id', 'gallery_variation_id', 'product_id', 'product_name', 'product_type_id',
						'moulding_id', 'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id',
						'mount__name', 'mount__color', 'mount_size', 'board_id', 'acrylic_id', 'stretch_id', 'image_width', 
						'image_height', 'moulding__width_inner_inches')
				'''
				gallery_variation_price = 0	
				a_cnt = 0
				prod_details = "Gallery Walls Set of " + str(g.set_of) + " artworks. Title: " + g.title + ". "
				prod_details = prod_details + "\nWhen hung as shown, covers area of approx " + str(gv.wall_area_width) + '" X ' + str(gv.wall_area_height) + '" inches on wall.'
				prod_details = prod_details + "Contains following artworks. "
				max_width = 0
				max_height = 0
				for gi in gallery_items:
					
					a_cnt = a_cnt + 1
					item_price = get_variation_item_price(gi.item_id)
					gallery_variation_price = gallery_variation_price + item_price

					item_total = round(gallery_variation_price + (gallery_variation_price * 20/100))
					item_total_mrp = round(item_total + (item_total * 20/100))
					
					p = Product_view.objects.filter(product_id = gi.product_id, product_type = gi.product_type_id).first()
					if Decimal(gi.image_width) > p.max_width or Decimal(gi.image_height) > p.max_height:
						update_delete = "Delete"

					item_length = int(gi.image_height)
					if gi.moulding_id:
						if gi.moulding.width_inner_inches:
							item_length = item_length + (gi.moulding.width_inner_inches * 2)
						if gi.mount_id:
							if gi.mount_size:
								item_length = item_length + (int(gi.mount_size) * 2)
					
					item_width = int(gi.image_width)
					if gi.moulding_id:
						if gi.moulding.width_inner_inches:
							item_width = item_width + (gi.moulding.width_inner_inches * 2)
						if gi.mount_id:
							if gi.mount_size:
								item_width = item_width + (int(gi.mount_size) * 2)			

						
					
					prod_details = prod_details + ' \n\n Artwork ' + str(a_cnt) 
					#+ ". Title: " + p.name + "."
					prod_details = prod_details + " \nPrint on: " + gi.print_medium_id.title()  + ", "
					prod_details = prod_details + " Print Size: " + str(gi.image_width) + " X " + str(gi.image_height) + "inch."

					incl_components = "One piece art, printed on " + gi.print_medium_id.title() + "; "
					incl_components = incl_components + "Print Size: " + str(gi.image_width) + " X " + str(gi.image_height) + "inch. "
					
					t_size = ''
					if gi.moulding:
						prod_details = prod_details + " \nFrame: " + gi.moulding.name + " (" + str(gi.moulding.width_inches) + " inch). Durable and very good finish." 
						incl_components = incl_components + "Frame: " + gi.moulding.name + " (" + str(gi.moulding.width_inches) + " inch)."
					if gi.mount:
						prod_details = prod_details + " \nMount: " + str(gi.mount_size) + " inch, Color: " + gi.mount.name.lower() + ". "
						incl_components =  incl_components + "Mount: " + str(gi.mount_size) + " inch, Color: " + gi.mount.name.lower() + ". "
					## Total Size
					t_size_width = int(gi.image_width)
					t_size_height = int(gi.image_height)
					if gi.moulding:
						if gi.moulding.width_inner_inches:
							t_size_width = t_size_width + gi.moulding.width_inner_inches *2
							t_size_height = t_size_height + gi.moulding.width_inner_inches * 2
					if gi.mount:
						t_size_width = t_size_width + gi.mount_size*2
						t_size_height = t_size_height + gi.mount_size*2

					if gi.print_medium_id.upper() == 'PAPER':
						prod_details = prod_details + " \n Covered with acrylic glass on top."
						incl_components = incl_components + "Acrylic covered. "
					else:
						if not gi.moulding:
							prod_details = prod_details + " \n Canvas wrapped over wooden frame at the back."
							incl_components = incl_components + "Canvas wrapped over wooden frame at the back."					
										
					#if gi.print_medium_id.upper() == 'PAPER':
					#	prod_details = prod_details + "\n\n Printed on NovaJet Matte Coated Premium Paper 230 (MCP 230)."
					#else:
					#	prod_details = prod_details + "\n\n Printed on NovaJet Artistic Matte Canvas 410 (AMC 410)."


					if t_size_width >= max_width:
						max_width = t_size_width
					if t_size_height >= max_height:
						max_height = t_size_height					
					
					t_size = str(t_size_width) + " X " + str(t_size_height) + " inch "
					prod_details = prod_details + " \n Finished Size: " + t_size

					prod_details = prod_details + " \n\n Comes with hooks and is ready for hanging."
						
				## Variation price
				item_total = round(gallery_variation_price + (gallery_variation_price * 20/100))
				item_total_mrp = round(item_total + (item_total * 20/100))

				search_terms = ( " panel paintings, wall paintings, wall art, paintings for home decor, art print, paintings with frame, paintings for living room, paintings for bed room, wall decor " )[:150]
				prod_img = g.room_view_url
				prod_name = 'Designer gallery wall art titled: ' + g.title + ' | Set of ' + str(g.set_of) + ' framed art prints'
				parentage = 'Child'
				variation = 'Variation'
				update_delete = 'update'
				col = ''
				col_map = 'Multi'
				p_size = 'Size: ' + str(gv.wall_area_width) + '" X ' + str(gv.wall_area_height) + '" inch'
				size_map = 'Medium'
				qty = '1000'
				item_total = item_total				
				color_name = ''
				occassion = ''
				finish_type = 'Matt finish'
				pattern_name = ''
				style_name = 'Gallery Wall'
				scent_name = ''
				power_source_type = ''
				packer_contact_information = ''
				packer_contact_name = ''
				target_audience_base = ''
				length_range = ''
				importer_contact_information = ''
				frame_type = 'Framed'
				theme = 'Mixed'
				department = ''
				item_volume = ''
				display_volume = ''
				sq_re = 'Rectangle'
			
				bullet1 = "A designer curated gallery wall set of " + str(g.set_of) + " artworks. "
				bullet1 = bullet1 + "When hung as shown, covers area of approximately " + str(gv.wall_area_width) + '" X ' + str(gv.wall_area_height) + '" inches on the wall.' 
				bullet2 = "Designer curated, premium quality gallery wall painting set with " + str(g.set_of) + " panels"
				bullet3 = "HD quality prints produced from licensed images, that don't fade for over 15 years, Polystyrene frames with classy finish"
				bullet4 = " All artworks in the a set are ready for hanging"


				if gv.is_parent:
					###########################################
					## CREATE PARENT ROW
					###########################################
					# Generate Amazon SKU Number
					sku_int = sku_int + 1
					amz_sku = sku_suf + str(sku_int)
					
					parentage = 'Parent'
					variation = ''					

					row_p =['wallart', amz_sku, "ARTE'VENUE", 
						'', '', prod_details, prod_name, '3749951031', 
						'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
						'https://www.artevenue.com' + settings.STATIC_URL + g.room_view_url, qty, 
						item_total if item_total > 0 else 0.01, 
						
						##Images
						'', '', '', '', '', '', '', '', '',
						
						## Variation
						variation, 'Size', '', parentage,  
							
						## Basic Info
						update_delete, "G:" + str(g.gallery_id) + "-" + str(gv.id), 'Montage Art Pvt Ltd', 
						'',
						
						## Discovery
						bullet1, bullet2, bullet3, bullet4, 
						'Your satisfaction is guaranteed.', 
						frame_type, search_terms, color_name, packer_contact_information,
						'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
						'', 
						'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',

						## - Diamensions
						'IN', 'IN', max_width, max_height, size_map, sq_re,
						'IN', 2, 'Count', g.set_of,
						
						## Fulfilment
						'IN', 3, str(t_size_width + 3),
						'KG', str(t_size_height + 3), 'IN', '', 'IN', 
						2, 

						
						##-- Compliance
						'FALSE', '', '',  
						'', '', '', '', '', '', '', '', '', '',
						'', '', '', '', '', '', '', '', '', '',
						'', '', '', '', '', '', '', '', '', '',

						##-- Offer
						'FALSE', 
						item_total if item_total > 0 else 0.01, item_total_mrp if item_total_mrp > 0 else 0.01,
						'', '12-31-2022',  'INR', 100, '', 
						'03/23/2021', '', 'A_GEN_REDUCED',
						'2', 'FALSE', 'New', '', item_total if item_total > 0 else 0.01, 
						'03/23/2021', '12/31/2022',
						
						##-- B2B
						'', '', '', '', '', '', '', ''
						]
						
					wr.writerow(row_p)
					
					parent_amz_sku = amz_sku
					### END PARENT ROW



				######################################
				### Child Row starts
				######################################
				update_delete = "Update"
				parentage = 'Child'
				variation = 'Variation'					
					
				# Generate Amazon SKU Number for the child row
				sku_int = sku_int + 1
				amz_sku = sku_suf + str(sku_int)

				'''
				## Create product image
				if gi.moulding_id:
					mld_id = gi.moulding_id
				else:
					mld_id = ''
				if gi.mount:
					mnt_color = gi.mount.color
					mnt_size = gi.mount_size
				else:
					mnt_color = ''
					mnt_size = 0 
				ids = [gi.product_id]
				create_images_by_prod_ids(ids, gi.product_type_id, amz_sku, gi.image_width, gi.image_height, mld_id, mnt_color, int(mnt_size), 'C')

				## Product Image location
				img_url = ''
				if env == 'DEV' or env == 'TESTING':
					img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "amazon_data/images/" 
					img_url = img_loc
				else:
					img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "amazon_data/images/"
					img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "amazon_data/images/"
				
				pos = p.url.rfind('/')
				loc = 0
				if pos > 0:
					loc = pos+1
				lowres_img_name = amz_sku +"_" + p.url[loc:]
				
				prod_img = (img_url + lowres_img_name)


				low_res_card1 = amz_sku +"_card1_" + p.url[loc:]
				card_1_img = (img_url + low_res_card1)				
				'''
	
				###################################################
				## Generate indivual product images in the gallery
				###################################################
				icnt = 0
				img_arr = {}
				for gi in gallery_items:
					icnt = icnt + 1
					p = Product_view.objects.filter(product_id = gi.product_id, product_type = gi.product_type_id).first()
					mld_id = 0
					mnt_color = '0'
					mnt_size = 0
					if gi.moulding:
						mld_id = gi.moulding_id
					else:
						mld_id = 0
					if gi.mount:
						mnt_color = gi.mount.color
						mnt_size = gi.mount_size
					else:
						mnt_color = '0'
						mnt_size = 0
					
					from django.http import HttpRequest
					request = HttpRequest()
					
					request.GET['prod_id'] = gi.product_id
					request.GET['moulding_id'] = mld_id
					request.GET['mount_color'] = mnt_color

					request.GET['mount_size'] = mnt_size
					request.GET['image_width'] = gi.image_width
					request.GET['prod_type'] = gi.product_type_id

					framed_img = get_FramedImage_by_id(request, gi.product_id, mld_id, mnt_color, 
							float(mnt_size), float(gi.image_width), gi.product_type_id )
					#framed_img = get_FramedImage(request)
					
					img_url = ''
					if env == 'DEV' or env == 'TESTING':
						img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "amazon_data/images/" 
						img_url = img_loc
					else:
						img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "amazon_data/images/"
						img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "amazon_data/images/"
					
					pos = p.url.rfind('/')
					loc = 0
					if pos > 0:
						loc = pos+1
					lowres_img_name = amz_sku +"_" + p.url[loc:]
					
					# save image
					ifile = Path(img_loc + lowres_img_name)
					if ifile.is_file():
						print("Image already available...skipping")
					else:
						framed_img.save(img_loc + lowres_img_name)
					
					img_arr[icnt] = img_url + lowres_img_name
				
				ilen = len(img_arr)
				if ilen < 8:					
					for x in range(ilen+1, 9):
						img_arr[x] = ''

				t_size = int(t_size_width) * int(t_size_height)
				if t_size <= 256:
					ship_weight = 1.25 * g.set_of
				elif t_size <= 576:
					ship_weight = 1.5 * g.set_of
				elif t_size <= 900:
					ship_weight = 2 * g.set_of
				elif t_size <= 1600:
					ship_weight = 2.5 * g.set_of
				else:
					ship_weight = 3 * g.set_of
		
				item_display_weight = ship_weight
					

				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"

				row_c =['wallart', amz_sku, "ARTE'VENUE", 
					'', '', prod_details, prod_name, '3749951031', 
					'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
					'https://www.artevenue.com' + settings.STATIC_URL + g.room_view_url, qty, 
					item_total if item_total > 0 else 0.01, 
					
					##Images
					img_arr[1], img_arr[2], img_arr[3], img_arr[4], img_arr[5], img_arr[6], img_arr[7], img_arr[8], '',
					
					## Variation
					variation, 'Size', parent_amz_sku, parentage,  
				
					## Basic Info
					update_delete, "G:" + str(g.gallery_id) + "-" + str(gv.id), 'Montage Art Pvt Ltd', 
					'',
					
					## Discovery
					bullet1, bullet2, bullet3, bullet4, 
					'Your satisfaction is guaranteed.', 
					frame_type, search_terms, color_name, packer_contact_information,
					'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
					'', 
					'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',

					## - Diamensions
					'IN', 'IN', max_width, max_height, size_map, sq_re,
					'IN', 2, 'Count', g.set_of,


					## Fulfilment
					'IN', 3, str(t_size_width + 3),
					'KG', str(t_size_height + 3), 'IN', '', 'IN', 
					ship_weight, 

					
					##-- Compliance
					'FALSE', '', '',  
					'', '', '', '', '', '', '', '', '', '',
					'', '', '', '', '', '', '', '', '', '',
					'', '', '', '', '', '', '', '', '', '',

					##-- Offer
					'FALSE', 
					item_total if item_total > 0 else 0.01, item_total_mrp if item_total_mrp > 0 else 0.01,
					'', '12-31-2022',  'INR', 100, '', 
					'03/23/2021', '', 'A_GEN_REDUCED',
					'2', 'FALSE', 'New', '', item_total if item_total > 0 else 0.01, 
					'03/23/2021', '12/31/2022',
					
					##-- B2B
					'', '', '', '', '', '', '', ''
					]
					
				wr.writerow(row_c)


def refresh_images():

	if env == 'PROD':
		cfile = '/home/artevenue/website/estore/static/feeds/single_img_prods_with_creative.csv'	
		amz_sku_file = '/home/artevenue/website/estore/static/feeds/amazon/amz_sku_file.csv'
	else:
		cfile = 'c:/artevenue/PRODUCT_FEEDS/single_img_prods_with_creative.csv'
		amz_sku_file = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/UPLOADS/amz_sku_file.csv'

	file = open(amz_sku_file)	
	sku_file = csv.reader(file, delimiter=',')	

	frame_names = {'18':'18_charcoalblack.png', '20':'20_saltwhite.png', '22':'22_umberbrown.png', '23_':'23_pecanbrown.png', '24':'24_midnightblack.png', '25':'25_chestnutbrown', '26':'26_slateblack', '8':'8_snowwhite' }
			
	## Collect all prod ids for non-gallery products with creatives
	non_g_prods = []
	with open(cfile) as nfile:
		non_g = csv.reader(nfile, delimiter=',')
		
		cnt = 0
		for n in non_g:
			cnt = cnt+1
			if cnt == 1:
				continue
			non_g_prods.append(n[0])

	img_url = ''
	if env == 'DEV' or env == 'TESTING':
		img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "amazon_data/images/" 
		img_url = img_loc
	else:
		img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "amazon_data/images/"
		img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "amazon_data/images/"
	
	
	with open(cfile) as ngal_file:
		non_gallery = csv.reader(ngal_file, delimiter=',')		
		
		for s in sku_file:
			sku = s[0]
			h = Amazon_data.objects.filter(amazon_sku = sku).first()		
			if h:
				if h.parent_child == 'P':
					continue
				prod_id = h.product_id
				m_id = h.moulding_id
				mount_color = h.mount_name
				mount_size = float(h.mount_size) if h.mount_size else 0
				stretch_id  = h.stretch_id

				img_2d_url = ''
				img_3d_url = ''
				creative_url = ''
				card1_url = ''
				card2_url = ''
				
				################################
				### 3D IMAGE 
				################################
				stretched_canvas = 'NO'
				if h.print_medium_id == 'CANVAS' and (m_id == None or m_id == '' or m_id == '0') and stretch_id == '1':
					stretched_canvas = 'YES'

				from django.http import HttpRequest
				request = HttpRequest()
				framed_img_3d = get_FramedImage_by_id(request, prod_id, m_id, mount_color=mount_color, 
					mount_size=float(mount_size), user_width=float(h.image_width), prod_type=h.product_type_id, 
					stretched_canvas=stretched_canvas, imgtilt='YES', dropshadow='NO' )
				
				aspect_ratio = framed_img_3d.width / framed_img_3d.height
				framed_img_3d = framed_img_3d.resize( (1200, int(round(1200/aspect_ratio))) )				
				
				pos = h.url.rfind('/')
				loc = 0
				if pos > 0:
					loc = pos+1
				img_3d_name = h.amazon_sku +"_3d_" + h.url[loc:]
				
				# save image
				ifile_3d = Path(img_loc + img_3d_name)
				#if ifile_3d.is_file():
				#	print("Image already available...skipping - Main image")
				#else:
				framed_img_3d.save(img_loc + img_3d_name)
				
				img_3d_url = img_loc + img_3d_name
				
				## Generate card images only for child rows
				if h.parent_child == 'C':

					## 2D Image
					request = HttpRequest()
					framed_img_2d = get_FramedImage_by_id(request, prod_id, m_id, mount_color=mount_color, 
						mount_size=float(mount_size), user_width=float(h.image_width), prod_type=h.product_type_id, 
						stretched_canvas=stretched_canvas, imgtilt='NO', dropshadow='NO' )

					aspect_ratio = framed_img_2d.width / framed_img_2d.height
					framed_img_2d = framed_img_2d.resize( (1200, int(round(1200/aspect_ratio))) )
					
					
					pos = h.url.rfind('/')
					loc = 0
					if pos > 0:
						loc = pos+1
					img_2d_name = h.amazon_sku +"_2d_" + h.url[loc:]
					
					# save image
					ifile_2d = Path(img_loc + img_2d_name)
					#if ifile_2d.is_file():
					#	print("Image already available...skipping - Main image")
					#else:
					framed_img_2d.save(img_loc + img_2d_name)

					img_2d_url = img_loc + img_2d_name
					
					## CREATIVE/ROOM VIEW Image
					## If this prod does not have a creative, then create dynamically 
					if h.product_id in non_g_prods:
						for n in non_gallery:
							if n[0] == p.product_id:
								creative_url = n[1]	
					else:
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
						request.GET['card_no'] = '2'
						card = get_catalog_card(request, False)
						creative_card = h.amazon_sku +"_creative_" + h.url[loc:]
						# save image
						c1file = Path(img_loc + creative_card)
						#if c1file.is_file():
						#	print("Image already available...skipping - Card 2")
						#else:
						card.save(img_loc + creative_card)
					
						creative_url = img_url + creative_card
						
								
				if h.parent_child == 'C':
				
					if h.print_medium_id == 'PAPER' and (h.mount_id != '' and h.mount_id != '0' and h.mount_size != 0) and (h.moulding_id != '' and h.moulding_id != '0') :
						card1_url = 'https://www.artevenue.com/static/img/prod_desc/paper_frame_mount.png'
					elif h.print_medium_id == 'PAPER' and (h.mount_id == '' or h.mount_id == '0') and (h.moulding_id != '' and h.moulding_id != '0'):
						card1_url = 'https://www.artevenue.com/static/img/prod_desc/paper_frame_no_mount.png'
					elif h.print_medium_id == 'CANVAS' and (h.moulding_id != '' and h.moulding_id != '0'):
						card1_url = 'https://www.artevenue.com/static/img/prod_desc/canvas_frame.png'
					elif h.print_medium_id == 'PAPER' and (h.mount_id == '' or h.mount_id == '0') and (h.moulding_id == '' or h.moulding_id == '0'):
						card1_url = 'https://www.artevenue.com/static/img/prod_desc/paper_print.png'
					elif h.print_medium_id == 'CANVAS' and (h.moulding_id == '' or h.moulding_id == '0') and h.stretch_id != '1':
						card1_url = 'https://www.artevenue.com/static/img/prod_desc/canvas_print.png'
					elif h.print_medium == 'CANVAS' and (h.moulding_id == '' or h.moulding_id == '0') and h.stretch_id == '1':
						card1_url = 'https://www.artevenue.com/static/img/prod_desc/canvas_stretched.png'
					else:
						card1_url = ''
					
					
					################################
					### FRAME
					################################					
					if h.moulding_id:						
						f_name = ""
						for k, v in frame_names.items():
							if k == h.moulding_id:
								fname = v
								break
						
						card2_url = 'https://www.artevenue.com/static/img/prod_desc/' + v
					
					## Save in urls table
					hf = Amazon_data.objects.filter(amazon_key = h.amazon_key).update(	
							framed_url = img_3d_url,
							card1_url = img_2d_url, 
							card2_url = creative_url,
							card3_url = card1_url,
							card4_url = card2_url
						) 						
					
				else:
					## Save in urls table
					hf = Amazon_data.objects.filter(amazon_key = h.amazon_key).update(	
							framed_url = img_2d_url)
					
				print("Saved: " + img_3d_url)




def amzFile_by_sku(file_loc=None):

	if not file_loc:
		if env == 'PROD':
			amz_sku_file = '/home/artevenue/website/estore/static/feeds/amazon/single_prod_creative_sku_file.csv'
		else:
			amz_sku_file = 'C:/artevenue/AMAZON/ARTEVENUE_Mar201/UPLOADS/single_prod_creative_sku_file.csv'	
	

	skus = []
	with open(amz_sku_file) as nfile:
		non_g = csv.reader(nfile, delimiter=',')		
		cnt = 0
		for n in non_g:
			cnt = cnt+1
			if cnt == 0:
				continue
			skus.append(n[0])	

	amz = Amazon_data.objects.filter(is_published = True,
		amazon_sku__in = skus
		).order_by('amazon_sku')	
	
	print("COUNT: " + str(amz.count()) )
		
	file_nm = 'av_amz_data_single_prod.csv'
	
	with open(file_nm, 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row =['product_type', 'Seller SKU', 'Brand', 'Product ID', 'Product ID Type',
			'Product Description', 
			'Item Name', 'Recommended Browse Nodes', 'Country Of Origin', 'HSN Code',
			'Maximum Retail Price', 'Main Image URL', 'Quantity', 'Standard Price', 
			
			## Images
			'Other Image URL1', 'Other Image URL2', 'Other Image URL3', 'Other Image URL4',
			'Other Image URL5', 'Other Image URL6', 'Other Image URL7', 'Other Image URL8',
			'Swatch Image URL', 

			## Variation
			'Relationship Type', 'Variation Theme', 'Parent SKU', 'Parentage',

			## Basic
			'Update Delete', 'Manufacturer Part Number', 'Manufacturer', 
			'Product Exemption Reason'

			## Discovery
			'Bullet Point1', 'Bullet Point2', 'Bullet Point3',
			'Bullet Point4', 'Bullet Point5', 'Frame Type', 'Search Terms', 
			'color Name', 'Packer', 'Item Type Name', 'Theme', 'Size', 'Color Map', 
			'Frame Material Type', 'Paint Type', 'Importer', 'Material Type',
			'Manufacturer Contact',
			
			## Dimensions
			'Item Width Unit of Measure', 'Item Height Unit of Measure', 'Item Width', 
			'Item Height', 'Size Map', 'Shape', 'Item Length Unit of Measure', 
			'Item Length', 'Unit Count Type', 'Unit Count',
			
			## Fulfilment
			'Package Height Unit of Measure', 'Package Length', 'Package Width',
			'Package Weight Unit of Measure', 'Package Height', 
			'Package Width Unit of Measure', 'Fulfilment Center ID',
			'Package Length Unit of Measure', 'Package Weight',
			
			#Compliance
			'Is This Product a Battery or uses Battery?', 
			'Batteries are Included', 'Battery Comosition',
			'Battery Type/Size 1', 'Battery Type/Size 2', 'Battery Type/Size 3', 
			'Number of Batteries 1',  'Number of Battaries 2', 'Number of Batteries 3', 
			'Battery Weight', 'Battery Weight Unit of Measure', 
			'Number of Lithium Metal Cells', 'Number of Lithium Ion Cells',
			'Lithium Battery Packaging', 'Watt Hours per Battery', 
			'Lithium Battery Energy Content Unit of Measure', 'Lithium content',
			'Lithium Battery Weigth Unit of Measure', 
			'Applicable Dangerous Goods Regulations1',
			'Applicable Dangerous Goods Regulations2',
			'Applicable Dangerous Goods Regulations3',
			'Applicable Dangerous Goods Regulations4',
			'Applicable Dangerous Goods Regulations5',
			#'UN Number', 'Safty Data Sheet URL', 			
			#'item Weight', 'Item Weight Unit of Measure', 
			#'Item Volume', 'Item Volume Unit of Measure',
			#'Flash Point (C)', 'Categorisation/GHS Pictogram1', 
			#'Categorisation/GHS Pictogram2',  'Categorisation/GHS Pictogram3', 
			
			## Offer
			'Is Giftwrap Avaiable?', 'Minimum Advertized Price', 'List Price',
			'Release Date', 'Offer End Date', 'Currency', 'Max Order Quantity',
			'Merchant Shipping Group Name',  'Offer Start Date', 'Restock Date',
			'Product Tax Code', 'Handling Time', 'Can Gift be Messaged?',
			'Condition', 'Condition Note', 'Sale Price', 
			'Sale Start Date', 'Sale End Date', 

			##B2B
			'Business Price', 'Quantity Price Type', 'Quantity Price 1', 
			'Quantity Lower Bound 1', 'Quantity Price 2', 
			'Quantity Lower Bound 2', 'Quantity Price 3', 'Quantity Lower Bound 3',
			'Quantity Price 4', 'Quantity Lower Bound 4', 'Quantity Price 5', 
			'Quantity Lower Bound 5', 'Pricing Action', 
			'United Nations Stadard Products and Service Code', 'National Stock Number'

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
				col_map = 'Multi'
				p_size = 'Size: ' + str(10) + '" X ' + str(10) + '" (inches)'
				size_map = ''
				qty = '1'
				item_total = 0
				parent_amz_sku = ''
				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"
			else:
				parentage = 'Child'
				variation = 'Variation'
				col = ''
				col_map = 'Multi'
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Print on ' + h.print_medium_id.title()
				size_map = 'Medium'
				qty = '1000'
				item_total = h.item_total
				parent_amz_sku = h.parent_amz_sku
				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"
			
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
			packer_contact_name = ''
			target_audience_base = ''
			length_range = ''
			importer_contact_information = ''
			frame_type = 'Framed'
			theme = cat
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
				
			row =['wallart', h.amazon_sku, "ARTE'VENUE", 
				'', '', prod_details, prod_name, '3749951031', 
				'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
				h.framed_url, qty, 
				item_total if item_total > 0 else 0.01, 
				
				##Images
				h.card1_url, h.card2_url, h.card3_url, h.card4_url, h.card5_url,
				'', '', '', '',
				
				## Variation
				variation, 'Size', parent_amz_sku, parentage,  
					
				## Basic Info
				update_delete, h.part_number, 'Montage Art Pvt Ltd', 
				'',
				
				## Discovery
				bullet1, bullet2, bullet3, 
				'Comes with hooks and is ready to be hung on the wall.', 
				'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
				frame_type, search_terms, color_name, packer_contact_information,
				'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
				h.print_medium_id.title(), 
				'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',

				## - Diamensions
				'IN', 'IN', t_size_width, t_size_height, size_map, sq_re,
				'IN', 2, 'Count', 1,

				## Fulfilment
				'IN', 3, str(t_size_width + 3),
				'KG', str(t_size_height + 3), 'IN', '', 'IN', 
				ship_weight, 
				
				##-- Compliance
				'FALSE', '', '',  
				'', '', '', '', '', '', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '',

				##-- Offer
				'FALSE', 
				item_total if item_total > 0 else 0.01, item_total_mrp if item_total_mrp > 0 else 0.01,
				'', '12-31-2022',  'INR', 100, '', 
				'03/23/2021', '', 'A_GEN_REDUCED',
				'2', 'FALSE', 'New', '', item_total if item_total > 0 else 0.01, 
				'03/23/2021', '12/31/2022',
				
				##-- B2B
				'', '', '', '', '', '', '', ''
				]
				
			wr.writerow(row)
				
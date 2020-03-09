from artevenue.models import Product_view, Moulding, Moulding_image, Mount
from artevenue.models import Stock_image_stock_image_category
from channelsales.models import Flipkart_data
from django.conf import settings
from decimal import Decimal

from PIL import Image, ImageFilter, ImageFile
import requests
from artevenue.views.product_views import *
from artevenue.views.tax_views import *
from artevenue.views.price_views import *
from artevenue.views import *

today = datetime.datetime.today()

def flipkart_data():
	##landscape_ids = [264794, 246920, 232260, 255409, 220235, 254133, 218493, 247803, 265654, 267538, 243158, 255411, 117791, 204401]
	floral_ids = [235444, 157496, 208355, 210840, 36137, 150212, 207291, 264553, 153125, 153129, 153102, 151536, 175434, 192519, 174947, 235444]

	curated = Curated_collection.objects.filter(product_id__in = floral_ids)
	createFlipkartData(curated)


def createFlipkartData(curated):	
	cnt = 0
	sku_suf = "FF" ## Floral
	sku_int = 100000  ## for Floral
	
	for c in curated:
		cnt = cnt + 1

		prod = Product_view.objects.get(product_id = c.product_id)

		if prod.is_published == False:
			continue

		if not prod:
			print( "No roduct found: ID = " + str(c.product_id) )
			return

		category = Stock_image_stock_image_category.objects.get(
			stock_image_id = c.product_id)
		category_id = category.stock_image_category_id
		quantity = 1
		
		grp_id = str(c.product_id)
		
		weight_unframed = 0.5
		
		#########################################################
		## Create 5 versions with different sizes
		#########################################################
		sizes = [12, 18, 24, 30, 36]

		for size in sizes:		
				
			if prod.orientation == 'Vertical' or prod.orientation == 'Square':
				img_width = size
				img_height = round(img_width / prod.aspect_ratio)
			else:
				img_width = size
				img_height = round(img_width / prod.aspect_ratio)
				##img_height = size
				##img_width = round(img_height * prod.aspect_ratio)			
					

			if img_width > prod.max_width or img_height > prod.max_height:
				continue



			#####################################
			#   Get the item price - UNFRAMED - PAPER
			#####################################
			price = get_prod_price(c.product_id, 
					prod_type= prod.product_type_id,
					image_width=img_width, 
					image_height=img_height,
					print_medium_id = 'PAPER',
					acrylic_id = 0,
					moulding_id = 0,
					mount_size = 0,
					mount_id = 0,
					board_id = 0,
					stretch_id = 0)
			item_price = price['item_price']
			msg = price['msg']
			cash_disc = price['cash_disc']
			percent_disc = price['percent_disc']
			item_unit_price = price['item_unit_price']
			item_disc_amt = price['disc_amt']
			disc_applied = price['disc_applied']
			promotion_id = price['promotion_id']
			#####################################
			# END::::    Get the item price
			#####################################	
			
			#####################################
			# 	if item price not found, return
			#####################################	
			if item_unit_price == 0 or item_unit_price is None:
				err_flg = True
				return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_quantity':quantity}, safe=False) )
			##################################################
			# END:	if item price not found, don't add to cart
			##################################################

			
			
			########################################################
			#	Calculate sub total, tax for the item
			########################################################
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
			########################################################
			#	END: Calculate sub total, tax for the item
			########################################################
			

			##############################################################
			# 	Get the product promotion details, if the item carries it
			##############################################################
			promo = {}
			if prod:
				promo = get_product_promotion(prod.product_id)	
			promotion = None
			if promo :
				if promo['promotion_id']:
					promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
			#####################################################
			# END:	Get the product promotion, if the item carries it
			#####################################################
			
			
			
			#####################################################
			# Generate Flipkart SKU Number
			#####################################################
			sku_int = sku_int + 1
			flk_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Flipkart SKU Number
			#####################################################
			
			#####################################################
			# Create Flipkart DATA
			#####################################################
			## Insert or Update
			promo_name = ''
			if promotion:
				promo_name = promotion.name
			hl = Flipkart_data(
				flk_sku = flk_sku,
				product_id = prod.product_id,
				product_name = prod.name,
				description = prod.description,
				part_number = prod.part_number,
				product_type = prod.product_type,
				category = category.stock_image_category,
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
				quantity = quantity,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = item_disc_amt,
				item_tax  = item_tax,
				item_total = item_price,
				moulding = None,
				moulding_size = 0,
				print_medium_id = 'PAPER',
				print_medium_size = 0,
				mount = None,
				mount_size = 0,
				board_id = None,
				board_size = 0,
				acrylic_id = None,
				acrylic_size = 0,
				stretch_id = None,
				stretch_size = 0,
				image_width = img_width,
				image_height = img_height,
				weight = weight_unframed,
				created_date = today,
				updated_date = today,
				group_id = grp_id,
			)
			hl.save()		




			moulding_id = 18 # Simple Black
				
			
			moulding = Moulding.objects.get( moulding_id = moulding_id )
			moulding_name = ''
			if moulding:
				moulding_name = moulding.name

			mount = Mount.objects.get(pk=3)   ## Offwhite
			mount_color = ''
			if mount :
				mount_color = mount.color
		
			if size < 30:
				moulding_id = 18
				mount_size = 1
			else:
				moulding_id = 24
				mount_size = 2

			weight = 1.5 if size == 12 else 2 if size == 18 else 2.5 if size == 24 else 4 if size == 30 else 5
				
			#####################################
			#         Get the item price
			#####################################
			price = get_prod_price(c.product_id, 
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
			#####################################
			# END::::    Get the item price
			#####################################	
			
			#####################################
			# 	if item price not found, return
			#####################################	
			if item_unit_price == 0 or item_unit_price is None:
				err_flg = True
				return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_quantity':quantity}, safe=False) )
			##################################################
			# END:	if item price not found, don't add to cart
			##################################################

			
			
			########################################################
			#	Calculate sub total, tax for the item
			########################################################
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
			########################################################
			#	END: Calculate sub total, tax for the item
			########################################################
			

			##############################################################
			# 	Get the product promotion details, if the item carries it
			##############################################################
			promo = {}
			if prod:
				promo = get_product_promotion(prod.product_id)	
			promotion = None
			if promo :
				if promo['promotion_id']:
					promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
			#####################################################
			# END:	Get the product promotion, if the item carries it
			#####################################################
			
			
			
			#####################################################
			# Generate Flipkart SKU Number
			#####################################################
			sku_int = sku_int + 1
			flk_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Flipkart SKU Number
			#####################################################
			
			#####################################################
			# Create Flipkart DATA
			#####################################################
			## Insert or Update
			promo_name = ''
			if promotion:
				promo_name = promotion.name
			hl = Flipkart_data(
				flk_sku = flk_sku,
				product_id = prod.product_id,
				product_name = prod.name,
				description = prod.description,
				part_number = prod.part_number,
				product_type = prod.product_type,
				category = category.stock_image_category,
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
				quantity = quantity,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = item_disc_amt,
				item_tax  = item_tax,
				item_total = item_price,
				moulding = moulding,
				moulding_size = 0,
				print_medium_id = 'PAPER',
				print_medium_size = 0,
				mount = mount,
				mount_size = mount_size,
				board_id = 1,
				board_size = 0,
				acrylic_id = 1,
				acrylic_size = 0,
				stretch_id = 1,
				stretch_size = 0,
				image_width = img_width,
				image_height = img_height,
				weight = weight,
				created_date = today,
				updated_date = today,
				group_id = grp_id,
			)
			hl.save()		
			
			
			

			#####################################
			#   Get the item price - UNFRAMED - CANVAS
			#####################################
			price = get_prod_price(c.product_id, 
					prod_type= prod.product_type_id,
					image_width=img_width, 
					image_height=img_height,
					print_medium_id = 'CANVAS',
					acrylic_id = 0,
					moulding_id = 0,
					mount_size = 0,
					mount_id = 0,
					board_id = 0,
					stretch_id = 0)
			item_price = price['item_price']
			msg = price['msg']
			cash_disc = price['cash_disc']
			percent_disc = price['percent_disc']
			item_unit_price = price['item_unit_price']
			item_disc_amt = price['disc_amt']
			disc_applied = price['disc_applied']
			promotion_id = price['promotion_id']
			#####################################
			# END::::    Get the item price
			#####################################	
			
			#####################################
			# 	if item price not found, return
			#####################################	
			if item_unit_price == 0 or item_unit_price is None:
				err_flg = True
				return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_quantity':quantity}, safe=False) )
			##################################################
			# END:	if item price not found, don't add to cart
			##################################################

			
			
			########################################################
			#	Calculate sub total, tax for the item
			########################################################
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
			########################################################
			#	END: Calculate sub total, tax for the item
			########################################################
			

			##############################################################
			# 	Get the product promotion details, if the item carries it
			##############################################################
			promo = {}
			if prod:
				promo = get_product_promotion(prod.product_id)	
			promotion = None
			if promo :
				if promo['promotion_id']:
					promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
			#####################################################
			# END:	Get the product promotion, if the item carries it
			#####################################################
			
			
			
			#####################################################
			# Generate Flipkart SKU Number
			#####################################################
			sku_int = sku_int + 1
			flk_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Flipkart SKU Number
			#####################################################
			
			#####################################################
			# Create Flipkart DATA
			#####################################################
			## Insert or Update
			promo_name = ''
			if promotion:
				promo_name = promotion.name
			hl = Flipkart_data(
				flk_sku = flk_sku,
				product_id = prod.product_id,
				product_name = prod.name,
				description = prod.description,
				part_number = prod.part_number,
				product_type = prod.product_type,
				category = category.stock_image_category,
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
				quantity = quantity,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = item_disc_amt,
				item_tax  = item_tax,
				item_total = item_price,
				moulding = None,
				moulding_size = 0,
				print_medium_id = 'CANVAS',
				print_medium_size = 0,
				mount = None,
				mount_size = 0,
				board_id = None,
				board_size = 0,
				acrylic_id = None,
				acrylic_size = 0,
				stretch_id = None,
				stretch_size = 0,
				image_width = img_width,
				image_height = img_height,
				weight = weight_unframed,
				created_date = today,
				updated_date = today,
				group_id = grp_id,
			)
			hl.save()		

			

			#####################################
			#         Get the item price
			#####################################
			price = get_prod_price(c.product_id, 
					prod_type= prod.product_type_id,
					image_width=img_width, 
					image_height=img_height,
					print_medium_id = 'CANVAS',
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
			#####################################
			# END::::    Get the item price
			#####################################	
			
			#####################################
			# 	if item price not found, return
			#####################################	
			if item_unit_price == 0 or item_unit_price is None:
				err_flg = True
				return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_quantity':quantity}, safe=False) )
			##################################################
			# END:	if item price not found, don't add to cart
			##################################################

			
			
			########################################################
			#	Calculate sub total, tax for the item
			########################################################
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
			########################################################
			#	END: Calculate sub total, tax for the item
			########################################################
			

			##############################################################
			# 	Get the product promotion details, if the item carries it
			##############################################################
			promo = {}
			if prod:
				promo = get_product_promotion(prod.product_id)	
			promotion = None
			if promo :
				if promo['promotion_id']:
					promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
			#####################################################
			# END:	Get the product promotion, if the item carries it
			#####################################################
			
			
			
			#####################################################
			# Generate Amazon SKU Number
			#####################################################
			sku_int = sku_int + 1
			flk_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Amazon SKU Number
			#####################################################
			
			#####################################################
			# Create Amazon DATA
			#####################################################
			## Insert or Update
			promo_name = ''
			if promotion:
				promo_name = promotion.name
			hl = Flipkart_data(
				flk_sku = flk_sku,
				product_id = prod.product_id,
				product_name = prod.name,
				description = prod.description,
				part_number = prod.part_number,
				product_type = prod.product_type,
				category = category.stock_image_category,
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
				quantity = quantity,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = item_disc_amt,
				item_tax  = item_tax,
				item_total = item_price,
				moulding = moulding,
				moulding_size = 0,
				print_medium_id = 'CANVAS',
				print_medium_size = 0,
				mount = None,
				mount_size = 0,
				board_id = 1,
				board_size = 0,
				acrylic_id = 1,
				acrylic_size = 0,
				stretch_id = 1,
				stretch_size = 0,
				image_width = img_width,
				image_height = img_height,
				weight = weight,				
				created_date = today,
				updated_date = today,
				group_id = grp_id,
			)
			hl.save()		

	
	print("Data creation/Update complete: Count - " + str(cnt) )

			
def createFlipkartFile():
	
	##ids = [9340,9341,32597,2598,42400,76998,76999,99947,99948,99949,153812,170876,170877,219076,252006,252029,252040,226234,226235,236091,32695,32696,42386,42383,42388,31809,31810,55175,55176,55177,119917,119918,119921,121675,121683,121685,198876,219771,220942,220493,221155,231333,231334,231335,234652,239355,254125,254126,254129]

	## Landscape Campaigns
	#ids = [264794, 246920, 232260, 255409, 220235, 254133, 218493, 247803, 265654, 267538, 243158, 255411, 117791, 204401]

	## Floral Campaigns
	ids = [235444, 157496, 208355, 210840, 36137, 150212, 207291, 264553, 153125, 153129, 153102, 151536, 175434, 192519, 174947, 235444]
	
	flk = Flipkart_data.objects.filter(is_published = True, product_id__in = ids,
		flk_sku__gte = 'AVC10001').order_by('flk_sku')
	with open('FlipkartTemplate.csv', 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row =['Seller SKU ID', 'Brand',	'Model Number',	'Painting Type', 'Painting Theme',
			'Width (inch)',	'Height (inch)', 'Weight (kg)',	'Pack of', 'Frame Included', 'Panel View', 
			'Main Image URL', 'Other Image URL 1', 'Other Image URL 2', 'Other Image URL 3', 'Group ID',
			'Model Name', 'Description', 'Sales Package','Key Features', 'Search Keywords',	
			'Video URL', 'Frame Color',	'Frame Material', 'Artist Name', 'Regional Speciality',	
			'Art Form Type', 'Wall Mount', 'Shape',	'Other Dimensions',	'Water Resistant',
			'Other Features', 'Domestic Warranty', 'Domestic Warranty - Measuring Unit',
			'International Warranty', 'International Warranty - Measuring Unit', 'Warranty Summary',
			'Warranty Service Type', 'Covered in Warranty',	'Not Covered in Warranty', 'Base Material',
			'Ink Type',	'Glass Frame', 'EAN/UPC', 'Size'

			
			]
		wr.writerow(row)
		
		curr_grp_id = ''
		first_loop = True
		for h in flk:
		
			## Skip unframed 
			if h.moulding is None:
				continue
		
		
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

			incl_components = "One piece art with frame, printed on " + h.print_medium_id.title() + "; "
			incl_components = incl_components + "Image Print Size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + "; "
			if h.moulding_id:
				prod_details = "Painting with frame," + " Title: " + h.product_name + ", Artist: " + h.artist + ".\nPrinted on: " + h.print_medium_id.title() + "; Framed Art Print. "
				bullet1 = 'Printed on ' + h.print_medium_id.title() + ', size: ' + str(formatNumber(h.image_width + (h.moulding.width_inner_inches *2) + (h.mount_size *2) )) + " X " + str(formatNumber(h.image_height + (h.moulding.width_inner_inches * 2) + ( h.mount_size * 2) )) + " inch. "
			else:
				prod_details = "Painting Title: " + h.product_name + ", Artist: " + h.artist + ".\nPrinted on: " + h.print_medium_id.title() + "; Unframed Art Print. Rolled and delivered in a tube."
				bullet1 = "Printed on " + h.print_medium_id.title() + ", size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + " inch. "

			prod_details = prod_details + "Image Size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + "; \n"

			if h.print_medium_id == 'PAPER':
				prod_details = prod_details + "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
			else:
				prod_details = prod_details + "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \n"
			bullet2 = ''
			t_size = ''
			if h.moulding_id:
				prod_details = prod_details + "Frame: " + h.moulding.name + " (" + str(formatNumber(h.moulding.width_inches)) + " inch). Frame is made of polystyrene, which is light weight, long lasting and has very good finish. \n"
				incl_components = incl_components + "Frame: " + h.moulding.name + " (" + str(formatNumber(h.moulding.width_inches)) + "inch, Polystyrene). "
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
			
			t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch"
			prod_details = prod_details + "Product Size: " + t_size 
			
			if h.moulding :
				prod_details = prod_details + ". \nIt comes with hooks at the back, ready to be hung on the wall."
				
			incl_components = incl_components + "Product Size: " + t_size
			
			bullet3 = ''
			if h.acrylic_id:
				if h.print_medium_id == "PAPER":
					incl_components = incl_components + "Acrylic covered; "
					bullet3 = "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility."
				else:
					bullet3 = "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions."
			#if i.stretch_id:
			#	prod_details = prod_details +  + "Canvas Stretched; "

			search_terms = ("home decor art painting with frame for living room, bed room wall " + h.key_words.replace('|', ' '))
			
			## Convert to upper case and remove duplicate words, limit to 150 chars
			search_terms = ' '.join(set(search_terms.upper().split()))[:150]
			
			if h.image_type == '0':
				if h.moulding :				
					prod_name = "Floral painting with frame, Title: " + h.product_name + '; Artist: ' + h.artist + '; Framed Art Print (' + t_size + ')'
				else:
					prod_name = "Floral painting, Title: " + h.product_name + '; Artist: ' + h.artist + '; Unframed Art Print (' + t_size + ')'		
			else:
				if h.moulding :				
					prod_name = "Floral art with frame, Title: " + h.product_name + '; Artist: ' + h.artist + ' - Framed Art Print(' + t_size + ')'
				else:
					prod_name = "Floral art, Title: " + h.product_name + '; Artist: ' + h.artist + ' - Unframed Art Print(' + t_size + ')'

			if h.print_medium_id == "PAPER":
				prod_name = prod_name + ", Printed on Paper"
			else:
				prod_name = prod_name + ", Printed on Canvas"
			
			if curr_grp_id == h.group_id:
				url = unframed_url
			else:
				url = h.framed_url
				unframed_url = url
				curr_grp_id = h.group_id
				
			row =[h.flk_sku, "MONTAGE", h.part_number, 'Digital Reprint', 'Floral', breadth, length,
				h.weight, 1, 'Yes', 'Single', url if h.moulding is None else h.framed_url, '', '', '', h.group_id, prod_name,
				prod_details, incl_components, bullet1 + ', ' +  bullet2 + ', ' + bullet3 + ' Custom made for you and ready to be hung on the wall.',
				search_terms, '', 'Black', 'Polystyrene', h.artist, '', '', 'Yes', 'Square/Rectangle',
				'', 'No', '', 1, 'Month', '', '', 'Carries 1 month domestic and international warranty against manufacturing defects',
				'Please email us picture of damage or other issues. After our inspection of the pictures, and our approval, please ship the products us and we will send the replacement.', 
				'Covers the art print and the frame', '', h.print_medium_id.title(), '', 
				'Yes' if h.print_medium_id == 'PAPER' and h.moulding else 'No', '', 'M'
				]
			
			wr.writerow(row)

def createFlipkartImages():

	flk_data = Flipkart_data.objects.filter(flk_sku__startswith = 'FF').order_by('flk_sku')  ## Floral
	for h in flk_data:
		image_width = h.image_width
		
		if h.moulding:
			if h.mount:
				framed_img = get_flk_FramedImage_api(h.product_id, h.moulding_id, 
					h.mount.color, h.mount_size, image_width)
			else:
				framed_img = get_flk_FramedImage_api(h.product_id, h.moulding_id, 
					None, h.mount_size, image_width)
				
			f_nm = "f_"
		else:
			framed_img = get_flk_FramedImage_api(h.product_id)
			f_nm = "n_"
			
		env = settings.EXEC_ENV
		img_url = ''
		if env == 'DEV' or env == 'TESTING':
			img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "flipkart_data/images/" 
			img_url = img_loc
		else:
			img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "flipkart_data/images/"
			img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "flipkart_data/images/"
		
		pos = h.url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		lowres_img_name = h.flk_sku +"_" + h.url[loc:]
		
		# save image
		framed_img.save(img_loc + lowres_img_name)
		
		## Save in urls table
		hf = Flipkart_data.objects.filter(flk_sku = h.flk_sku).update(	
				framed_url = img_url + lowres_img_name)
		
		print("Saved: " + lowres_img_name)

def get_flk_FramedImage_api(prod_id, frame_id=None, mount_color=None, mount_size=None, user_width=None):

	# Get image
	prod_img = Stock_image.objects.filter( product_id = prod_id ).first()		
	env = settings.EXEC_ENV

	if env == 'DEV' or env == 'TESTING':
		response = requests.get(prod_img.url)
		img_source = Image.open(BytesIO(response.content))
	else:
		img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)			
	
	## If no frame ID, return image without frame
	if not frame_id:
		return img_source
	
	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = frame_id, image_type = "APPLY").values(
				'url', 'moulding__width_inches', 'border_slice').first()
	
	if moulding:
		m_width_inch = Decimal(moulding['moulding__width_inches'])
		
		# Image width displayed in browser in inches
		disp_inch = 450//96		
		ratio = disp_inch / user_width
		border = int(m_width_inch * ratio * 96)
		
		border = int(m_width_inch * 450 / user_width)
		
		m_size = int(mount_size * 96 * ratio)
		
		
		from django.http import HttpRequest
		request = HttpRequest()
		request.method = 'GET'
		
		if m_size > 0 and mount_color != '' and mount_color != '0' and mount_color != 'None':

			img_with_mount = image_views.addMount(img_source, mount_color, m_size, m_size, m_size, m_size)
						
			framed_img = image_views.applyBorder( request, img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
		else:
			framed_img = image_views.applyBorder( request, img_source, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
	else :
		# No moulding, returing the image as it is.
		framed_img = Image.new("RGB", (img_source.width, img_source.height), 0)
		framed_img.paste(img_source, (0,0))		
	
	return framed_img

def formatNumber(num):
	if num % 1 == 0:
		return int(num)
	else:
		return num
		
		
		
def createSellingInfoFile():
	## Floral Campaigns
	ids = [235444, 157496, 208355, 210840, 36137, 150212, 207291, 264553, 153125, 153129, 153102, 151536, 175434, 192519, 174947, 235444]
	
	flk = Flipkart_data.objects.filter(is_published = True, product_id__in = ids,
		flk_sku__gte = 'AVC10001').order_by('flk_sku')
	with open('FlipkartTemplate_sellingInfo.csv', 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		head_row =['sku', 'MRP','Your Selling Price','Ignore warnings','USUAL PRICE','Local Delivery Charge to Customer (per qty)',
			'Zonal Delivery Charge to Customer (per qty)','National Delivery Charge to Customer (per qty)',
			'Selling Region Restriction','System Stock count','Your Stock Count','Procurement SLA',
			'Listing Status','Inactive Reason','Fulfillment By','Package Length - Length of the package in cms',
			'Package Breadth - Breadth of the package in cms','Package Height - Height of the package in cms',
			'Package Weight - Weight of the package in Kgs','Procurement Type',
			'Harmonized System Nomenclature - HSN',	'Tax Code',	'Luxury Cess Tax Rate',
			'Manufacturer Details',	'Importer Details',	'Packer Details','Country of Origin ISO code',	
			'Date of Manufacture in dd/MM/yyyy', 'Shelf Life in Months'
		]
			
		wr.writerow(head_row)
		
		for h in flk:
		
			## Skip unframed 
			if h.moulding is None:
				continue			

			t_size = ''
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
			
			t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch"
			
						
			row = [ h.flk_sku, h.item_total, h.item_total, 'YES', h.item_total, 0 ,0 ,0, None, None, 1000, 2, 'Active',
					None, 'Seller', (t_size_width + 3) * Decimal(2.54), (t_size_height + 3) * Decimal(2.54),
					3 * Decimal(2.54), h.weight, None, '9702', 'GST_12', None, 
					'Montage Art and Framing, 54 Vittal Mallya Road, Bangalore 560001, Phone: 9611503626',
					'', 'Montage Art and Framing, 54 Vittal Mallya Road, Bangalore 560001, Phone: 9611503626',
					'IN', today.strftime("%d/%m/%Y"), '60'
				]

			wr.writerow(row)

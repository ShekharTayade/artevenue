from artevenue.models import Product_view, Moulding, Moulding_image
from artevenue.models import Curated_collection, Mount
from artevenue.models import Homelane_data, Stock_image_stock_image_category
from django.conf import settings
from decimal import Decimal

from PIL import Image, ImageFilter
import requests
from .product_views import *
from .tax_views import *
from .price_views import *
from artevenue.views import *

import requests
from io import BytesIO

def createHomelaneData():
	
	## Get data from curated collections
	curated = Curated_collection.objects.all()
	cnt = 0
	for c in curated:
		cnt = cnt + 1
		if cnt >= 5000:
			break;
		
		prod = Product_view.objects.get(product_id = c.product_id)
		if not prod:
			print( "No roduct found: ID = " + str(c.product_id) )
			return
		
		if (cnt % 2) == 0:
			moulding_id = 18
			img_width = 12
			mount_size = 2
		else:
			moulding_id = 1   ## To be replaced with correct id
			img_width = 24
			mount_size = 1

		img_height = round(img_width / prod.aspect_ratio)
		moulding = Moulding.objects.get( moulding_id = moulding_id )

		mount = Mount.objects.get(pk=3)   ## Offwhite
		category = Stock_image_stock_image_category.objects.get(
			stock_image_id = c.product_id)
		category_id = category.stock_image_category_id
		quantity = 1
		
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
		promotion = {}
		if promo :
			if promo['promotion_id']:
				promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
		#####################################################
		# END:	Get the product promotion, if the item carries it
		#####################################################
		
		
		
		#####################################################
		# Create HomeLane DATA
		#####################################################
		## Insert or Update
		hl = Homelane_data(
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
			promotion_name = promotion.name,
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
			mount_name = mount.color,
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
			updated_date = today
		)
		hl.save()		
	
	print("Data creation/Update complete: Count - " + str(cnt) )

def createHomelaneImages():	
	homelane_data = Homelane_data.objects.all()
	for h in homelane_data:
		framed_img = get_FramedImage(h.product_id, h.moulding_id, 
			h.mount.color, h.mount_size, h.image_width)

		env = settings.EXEC_ENV
		if env == 'DEV' or env == 'TESTING':
			img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "homelane_data/images" 
		else:
			img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "homelane_data/images" 
		
		pos = h.url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		lowres_img_name = h.url[loc:]
		
		# save image
		framed_img.save(img_loc + lowres_img_name)
		
		## Create thumbnail and save
		framed_img.thumbnail( (75, 75) )
		pos = h.thumbnail_url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		thumb_img_name = h.thumbnail_url[loc:]
		framed_img.save(img_loc + thumb_img_name)

		
		## Save in urls table
		hf = Homelane_data.objects.filter(product_id = h.product_id).update(	
				framed_url = img_loc + lowres_img_name, 
				framed_thumbnail_url = img_loc + thumb_img_name)
		
		print("Saved: " + lowres_img_name)

def get_FramedImage(prod_id, frame_id, mount_color, mount_size, user_width):

	# Get image
	prod_img = Stock_image.objects.filter( product_id = prod_id ).first()		
	env = settings.EXEC_ENV

	if env == 'DEV' or env == 'TESTING':
		response = requests.get(prod_img.url)
		img_source = Image.open(BytesIO(response.content))
	else:
		img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)			
	
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
	
	framed_img = dropShadow(framed_img)

	return framed_img

def Homelane_endpoint_test():

	import json
	import urllib
	
	endpoint = "http://localhost:7000/homelane"
	json_url = urllib.request.urlopen(endpoint) 
	data = json.loads(json_url.read())	
	
	print(data)
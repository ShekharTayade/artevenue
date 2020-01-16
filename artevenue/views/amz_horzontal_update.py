from artevenue.models import Product_view, Moulding, Moulding_image
from artevenue.models import Curated_collection, Mount
from artevenue.models import Amazon_data, Stock_image_stock_image_category
from django.conf import settings
from decimal import Decimal

from PIL import Image, ImageFilter, ImageFile
import requests
from .product_views import *
from .tax_views import *
from .price_views import *
from artevenue.views import *

def updateAmazonData_width():
	
	amz = Amazon_data.objects.filter(pk = 36172, orientation = 'Horizontal')
	
	for c in amz:
		if c.parent_child == 'P':
			continue
	
		img_height = c.image_height
		img_width = round(img_height * c.aspect_ratio)
		quantity = 1
		#####################################
		#         Get the item price
		#####################################
		price = get_prod_price(c.product_id, 
				prod_type= c.product_type_id,
				image_width=img_width, 
				image_height=img_height,
				print_medium_id = 'PAPER',
				acrylic_id = 1,
				moulding_id = c.moulding_id,
				mount_size = c.mount_size,
				mount_id = c.mount_id,
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
			return 'Price not avaiable for this image'
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
		if c.product_type_id == 'STOCK-IMAGE':
			tax_rate = taxes['stock_image_tax_rate']
		if c.product_type_id == 'ORIGINAL-ART':
			tax_rate = taxes['original_art_tax_rate']
		if c.product_type_id == 'USER-IMAGE':
			tax_rate = taxes['user_image_tax_rate']
		if c.product_type_id == 'STOCK-COLLAGE':
			tax_rate = taxes['stock_image_tax_rate']
		if c.product_type_id == 'FRAME':
			tax_rate = taxes['frame_tax_rate']	
			
		# Calculate tax and sub_total
		item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
		item_tax = round( (item_price*quantity) - item_sub_total )
		########################################################
		#	END: Calculate sub total, tax for the item
		########################################################

		hl = Amazon_data.objects.filter( amazon_key = c.amazon_key ).update( 
				image_width = img_width,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = item_disc_amt,
				item_tax  = item_tax,
				item_total = item_price
			)
	
		return ''
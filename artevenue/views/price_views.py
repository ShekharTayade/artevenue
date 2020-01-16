from artevenue.views import product_views
from .frame_views import *
from artevenue.models import Stock_image, Publisher_price, Product_view, Moulding

from .tax_views import *
from decimal import Decimal

def get_prod_price(prod_id,**kwargs):
	prod_type = kwargs['prod_type']
	image_width = Decimal(kwargs['image_width'])
	image_height = Decimal(kwargs['image_height'])
	print_medium_id = kwargs['print_medium_id']
	acrylic_id = kwargs['acrylic_id']
	moulding_id = kwargs['moulding_id']
	mount_size = kwargs['mount_size']
	mount_id = kwargs['mount_id']
	board_id = kwargs['board_id']
	stretch_id = kwargs['stretch_id']
	msg = "SUCCESS"

	
	if prod_type == 'STOCK-IMAGE' or prod_type == 'USER-IMAGE':
		# Get image price on paper and canvas
		per_sqinch_price = get_per_sqinch_price(prod_id, prod_type)
		per_sqinch_paper = per_sqinch_price['per_sqin_paper']
		per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']	
				
		# Image Price
		if image_width:
			if image_width > 0 and image_height > 0:
				msg = "SUCCESS"
			else :
				msg = "ERROR-Image size missing"

		# Get the Item Price
		item_price = 0
		image_price = 0
		if print_medium_id == "PAPER":
			if per_sqinch_paper == 0:
				return ({"msg":msg, "item_price" : 0, 'cash_disc':0,
							'percent_disc':0, 'item_unit_price':0,
							'disc_amt':0, 'disc_applied':False, 'promotion_id':''})	
				
			# Image price
			if image_width > 0 and image_height > 0:
				'''
				image_price = image_width * image_height * per_sqinch_paper
				item_price = Decimal(item_price + image_price)
				'''
				item_price = get_price_reduction_by_size(per_sqinch_paper, image_width * image_height)
			
			# Acrylic Price	
			if acrylic_id:
				acrylic_price = image_width * image_height * get_acrylic_price_by_id(acrylic_id)
				item_price = Decimal(item_price + acrylic_price)
			
			# Moulding price
			if moulding_id:
				moulding_price = (image_width + image_height) * 2 * get_moulding_price_by_id(moulding_id)
				item_price = Decimal(item_price + moulding_price)

			# Mount price
			if mount_size and mount_id:
				mount_price = ((image_width + image_height) * 2 * Decimal(mount_size))  * get_mount_price_by_id(mount_id)
				item_price = Decimal(item_price + mount_price)
			
			# Board price
			if board_id:
				board_price = image_width * image_height * Decimal(get_board_price_by_id(board_id))
				item_price = Decimal(item_price + board_price)			
			
		elif print_medium_id == "CANVAS":
			if per_sqinch_canvas == 0:
				return ({"msg":msg, "item_price" : 0, 'cash_disc':0,
							'percent_disc':0, 'item_unit_price':0,
							'disc_amt':0, 'disc_applied':False, 'promotion_id':''})	

			# Image price
			#if image_width > 0 and image_height > 0:
			#	image_price = image_width * image_height * per_sqinch_canvas
			#	item_price = Decimal(item_price + image_price)
			#	print( "Image Price: " + str(image_price))
				
			if image_width > 0 and image_height > 0:
					'''
					image_price = image_width * image_height * per_sqinch_paper
					item_price = Decimal(item_price + image_price)
					'''
					item_price = get_price_reduction_by_size(per_sqinch_canvas, image_width * image_height)


			# Moulding price
			if moulding_id:
				moulding_price = (image_width + image_height) * 2 * get_moulding_price_by_id(moulding_id)
				item_price = Decimal(item_price + moulding_price)
			
			# Stretch price
			if stretch_id:			
				stretch_price = image_width * image_height * get_stretch_price_by_id(stretch_id)
				item_price = Decimal(item_price + stretch_price)
	
	else:
		prod = Product_view.objects.filter(product_id = prod_id, 
				product_type_id = prod_type).first()

		per_sqinch_price = get_per_sqinch_price(prod_id, prod_type)
		per_sqinch_paper = per_sqinch_price['per_sqin_paper']
		per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']	

		if print_medium_id == "PAPER":
			image_price = image_width * image_height * per_sqinch_paper
		else:
			image_price = image_width * image_height * per_sqinch_canvas
		
		item_price = Decimal(item_price + image_price)
		
		#item_price = prod.price
		#image_width = prod.art_width
		#image_height = prod.art_height
		
		# Moulding price
		if moulding_id:
			moulding_price = (image_width + image_height) * 2 * get_moulding_price_by_id(moulding_id)
			item_price = Decimal(item_price + moulding_price)

		# Mount price
		if mount_size and mount_id:
			mount_price = ((image_width + image_height) * 2 * Decimal(mount_size))  * get_mount_price_by_id(mount_id)
			item_price = Decimal(item_price + mount_price)
			
		
	
	item_price = Decimal(round(float(item_price),-1))
	
	##item_price_withoutdisc = Decimal( "{:.0f}".format( round(item_price, -1) ) )
	#item_price_withoutdisc = Decimal( round(float(item_price), -1) )
	
	disc_applied = False
	promo = product_views.get_product_promotion(prod_id, prod_type)
		
	disc_amt = 0
	cash_disc = 0
	if promo:
		cash_disc = round(promo['cash_disc'])
		percent_disc = promo['percent_disc']	
		promotion_id = promo['promotion_id']
	else:
		cash_disc = 0
		percent_disc = 0	
		promotion_id = ''
	
	if cash_disc > 0:
		item_price = item_price - cash_disc
		disc_applied = True
		disc_amt = round(cash_disc)
	elif percent_disc > 0:
		disc_amt = round(item_price * percent_disc / 100)
		item_price = item_price - disc_amt
		disc_applied = True


	###############################
	## Unit price (without tax)
	###############################
	# Get Tax
	item_tax = 0
	taxes = get_taxes()

	if prod_type == 'STOCK-IMAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod_type == 'ORIGINAL-ART':
		tax_rate = taxes['original_art_tax_rate']
	if prod_type == 'USER-IMAGE':
		tax_rate = taxes['user_image_tax_rate']
	if prod_type == 'STOCK-COLLAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod_type == 'FRAME':
		tax_rate = taxes['frame_tax_rate']
	
	item_unit_price = round( item_price / (1 + (tax_rate/100)), 2 )

	return ({"msg":msg, "item_price" : item_price, 'cash_disc':cash_disc,
				'percent_disc':percent_disc, 'item_unit_price':item_unit_price,
				'disc_amt':disc_amt, 'disc_applied':disc_applied, 'promotion_id':promotion_id})	

	
		
def get_per_sqinch_price(prod_id, prod_type):
	per_sqin_paper = 0
	per_sqin_canvas = 0
	if prod_type == 'STOCK-IMAGE':

		prod = Stock_image.objects.filter(product_id = prod_id).first()
		publisher_price = Publisher_price.objects.filter(publisher_id = prod.publisher )
		
		for p in publisher_price:
			if p.print_medium_id == "PAPER" :
				per_sqin_paper = p.price
			if p.print_medium_id == "CANVAS" :
				per_sqin_canvas = p.price
			
	elif prod_type == 'USER-IMAGE':
		per_sqin_paper = Decimal(1.3)
		per_sqin_canvas = Decimal(2.7)
	
	return ({'per_sqin_paper':per_sqin_paper, 'per_sqin_canvas' : per_sqin_canvas})


def get_price_reduction_by_size(price, size):

	size = float(size)
	price = float(price)
	slab1_start = 1300
	slab1_end = 1799
	slab1_reduction = 10 / (1799 - 1300)
	slab2_start = 1800
	slab2_end = 2399
	slab2_reduction = 5 / (2399 - 1800)
	slab3_start = 2400 
	slab3_end = 3456
	slab3_reduction = 5 / (3546 - 2400)

	slab4_start = 3457
	slab4_end = 5000
	slab4_reduction = 5 / (5000 - 3547)

	if size <= 1299:
		reduced_price = (price * size)  ## no reduction
	elif size  > 1299 and size < 1800:	
		reduction_factor = (size - 1300) * slab1_reduction
		reduced_price = (price * size) - (price * size * reduction_factor/100)				
	elif size < 2400:
		reduction_factor = (size - 1800) * slab2_reduction		
		reduced_price = (price * size) - (price * size * 10/100) - (price * size * reduction_factor/100)
	elif size < 3456:
		reduction_factor = (size - 2400) * slab3_reduction
		reduced_price = (price * size) - (price * size * 15/100) - (price * size * reduction_factor/100)
	else:
		reduction_factor = (size - 3456) * slab4_reduction
		reduced_price = (price * size) - (price * size * 20/100) - (price * size * reduction_factor/100)
		'''
		print("slab_Red" + str(slab4_reduction))
		print("Orig Price" + str(size*price))
		print("Reduction factor: " + str(reduction_factor))
		print("Reduction: " + str(price * size * reduction_factor/100) )	
		'''
	return round(reduced_price)


def get_price_for_6_prods(prod_id, aspect_ratio, prod_type='STOCK-IMAGE'):
	
	STANDARD_PROD_WIDTHS = [12, 18, 24, 30, 36, 42]
	
	# Get image price on paper and canvas
	per_sqinch_price = get_per_sqinch_price(prod_id, prod_type)
	per_sqinch_paper = per_sqinch_price['per_sqin_paper']
	per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']	

	try:
		product = Stock_image.objects.get(product_id = prod_id)
		
	except Stock_image.DoesNotExists:
		return ({'size_price_paper':0, 'size_price_canvas':0})
		
	## Common pricing components
	acrylic_id = 1
	moulding_id = 18  # Simple Black
	mount_id = 3 # Offwhite
	board_id = 1
	stretch_id = 1	
	
	size_price_paper = {}
	size_price_canvas = {}
	
	## Six prods with PAPER medium
	for i in STANDARD_PROD_WIDTHS:
	
		if i > product.max_width:
			continue
			
		p_data_paper = {}
		p_data_canvas = {}
		image_width = i
		image_height = round(image_width / aspect_ratio)

		mount_size = 1 if i <= 24 else 2 if i <= 42 else 3
		
		############################
		## PAPER
		############################
		item_price = get_price_reduction_by_size(per_sqinch_paper, image_width * image_height)

		p_data_paper['PAPER_WIDTH_UNFRAMED'] = image_width
		p_data_paper['PAPER_HEIGHT_UNFRAMED'] = image_height
		p_data_paper['PAPER_PRICE_UNFRAMED'] = Decimal(round(float(item_price),-1))
		
		# Acrylic Price	
		if acrylic_id:
			acrylic_price = image_width * image_height * get_acrylic_price_by_id(acrylic_id)
			item_price = Decimal(item_price + acrylic_price)
		
		# Moulding price
		if moulding_id:
			moulding_price = (image_width + image_height) * 2 * get_moulding_price_by_id(moulding_id)
			item_price = Decimal(item_price + moulding_price)

		# Mount price
		if mount_size and mount_id:
			mount_price = ((image_width + image_height) * 2 * Decimal(mount_size))  * get_mount_price_by_id(mount_id)
			item_price = Decimal(item_price + mount_price)
		
		# Board price
		if board_id:
			board_price = image_width * image_height * Decimal(get_board_price_by_id(board_id))
			item_price = Decimal(item_price + board_price)			
		
		moulding = Moulding.objects.get(pk = moulding_id)
		i_width = image_width + moulding.width_inner_inches * 2 + mount_size * 2
		i_height = image_height + moulding.width_inner_inches * 2 + mount_size * 2
		p_data_paper['PAPER_WIDTH'] = i_width
		p_data_paper['PAPER_HEIGHT'] = i_height
		p_data_paper['PAPER_PRICE'] = Decimal(round(float(item_price),-1))
		size_price_paper[str(i)] = p_data_paper

		############################
		## CANVAS
		############################
		if image_width > 0 and image_height > 0:
			item_price = get_price_reduction_by_size(per_sqinch_canvas, image_width * image_height)

		p_data_canvas['CANVAS_WIDTH_UNFRAMED'] = image_width
		p_data_canvas['CANVAS_HEIGHT_UNFRAMED'] = image_height
		p_data_canvas['CANVAS_PRICE_UNFRAMED'] = Decimal(round(float(item_price),-1))

		# Moulding price
		if moulding_id:
			moulding_price = (image_width + image_height) * 2 * get_moulding_price_by_id(moulding_id)
			item_price = Decimal(item_price + moulding_price)
		
		# Stretch price
		if stretch_id:			
			stretch_price = image_width * image_height * get_stretch_price_by_id(stretch_id)
			item_price = Decimal(item_price + stretch_price)

		i_width = image_width + moulding.width_inner_inches * 2
		i_height = image_height + moulding.width_inner_inches * 2
		p_data_canvas['CANVAS_WIDTH'] = i_width
		p_data_canvas['CANVAS_HEIGHT'] = i_height
		p_data_canvas['CANVAS_PRICE'] = Decimal(round(float(item_price),-1))
		size_price_canvas[str(i)] = p_data_canvas
		
	return ({'size_price_paper':size_price_paper, 'size_price_canvas':size_price_canvas})

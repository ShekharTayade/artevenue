from artevenue.views import product_views
from .frame_views import *
from artevenue.models import Stock_image, Publisher_price


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
		# Image price
		if image_width > 0 and image_height > 0:
			image_price = image_width * image_height * per_sqinch_paper
			item_price = Decimal(item_price + image_price)


		print( "Width: " + str(image_width) )
		print( "height: " + str(image_height) )
		print( "Image Price: " + str(image_price) )
		
		# Acrylic Price	
		if acrylic_id:
			acrylic_price = image_width * image_height * get_acrylic_price_by_id(acrylic_id)
			item_price = Decimal(item_price + acrylic_price)
			print( "Acrylic Price: " + str(acrylic_price))
		
		# Moulding price
		if moulding_id:
			moulding_price = (image_width + image_height) * 2 * get_moulding_price_by_id(moulding_id)
			item_price = Decimal(item_price + moulding_price)
			print( "Moulding Price: " + str(moulding_price))

		# Mount price
		if mount_size and mount_id:
			mount_price = ((image_width + image_height) * 2 * Decimal(mount_size))  * get_mount_price_by_id(mount_id)
			item_price = Decimal(item_price + mount_price)
			print( "Mount Price: " + str(mount_price))
		
		# Board price
		if board_id:
			board_price = image_width * image_height * Decimal(get_board_price_by_id(board_id))
			item_price = Decimal(item_price + board_price)
			print( "Board Price: " + str(board_price))

		print( "======================")
		print( "Total Item Price: " + str(item_price))
		
		
	elif print_medium_id == "CANVAS":

		# Image price
		if image_width > 0 and image_height > 0:
			image_price = image_width * image_height * per_sqinch_canvas
			item_price = Decimal(item_price + image_price)
			print( "Image Price: " + str(image_price))

		# Moulding price
		if moulding_id:
			moulding_price = (image_width + image_height) * 2 * get_moulding_price_by_id(moulding_id)
			item_price = Decimal(item_price + moulding_price)
			print( "Moulding Price: " + str(moulding_price))
		
		# Stretch price
		if stretch_id:			
			stretch_price = image_width * image_height * get_stretch_price_by_id(stretch_id)
			item_price = Decimal(item_price + stretch_price)
			print( "Stretch Price: " + str(stretch_price))

		print( "======================")
		print( "Total Item Price: " + str(item_price))

	item_price = Decimal(round(float(item_price),-1))

	#item_price_withoutdisc = Decimal( "{:.0f}".format( round(item_price, -1) ) )
	item_price_withoutdisc = Decimal( round(float(item_price), -1) )
	
	disc_applied = False
	promo = product_views.get_product_promotion(prod_id)
	print(promo)
	
	
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
		
	print( "======================")
	print( "Disc Amt: " + str(disc_amt))
	print( "Item Price: " + str(item_price))
	print( "Item Price w/o Disc: " + str(item_price_withoutdisc))

	return ({"msg":msg, "item_price" : item_price, 'cash_disc':cash_disc,
				'percent_disc':percent_disc, 'item_unit_price':item_price_withoutdisc,
				'disc_amt':disc_amt, 'disc_applied':disc_applied, 'promotion_id':promotion_id})	

	
		
def get_per_sqinch_price(prod_id, prod_type):

	if prod_type == 'STOCK-IMAGE':

		prod = Stock_image.objects.filter(product_id = prod_id).first()
		publisher_price = Publisher_price.objects.filter(publisher_id = prod.publisher )
		
		per_sqin_paper = 0
		per_sqin_canvas = 0
		for p in publisher_price:
			if p.print_medium_id == "PAPER" :
				per_sqin_paper = p.price
			if p.print_medium_id == "CANVAS" :
				per_sqin_canvas = p.price
				
	elif prod_type == 'USER-IMAGE':
		per_sqin_paper = Decimal(1.3)
		per_sqin_canvas = Decimal(2.7)
	 
	 
	return ({'per_sqin_paper':per_sqin_paper, 'per_sqin_canvas' : per_sqin_canvas})


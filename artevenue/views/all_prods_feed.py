from artevenue.models import Moulding, Mount, Curated_collection
from artevenue.models import Stock_image, Stock_image_stock_image_category
from gallerywalls.models import Gallery, Gallery_variation, Gallery_item
from decimal import Decimal
import csv
from .tax_views import *
from .price_views import *
from artevenue.views import *
from gallerywalls.views import *

from django.conf import settings

env = settings.EXEC_ENV
if env == 'PROD':
	fb_file_nm = '/home/artevenue/website/estore/static/feeds/facebook/facebook_feed_all_prods.csv'
	fb_ad_file_nm = '/home/artevenue/website/estore/static/feeds/facebook/facebook_feed_ad_prods.csv'
	fb_ad_in = '/home/artevenue/website/estore/static/feeds/facebook/fb_ad_prods_input.csv'
	google_file_nm = '/home/artevenue/website/estore/static/feeds/google/google_feed_all_prods.csv'
	google_ad_file_nm = '/home/artevenue/website/estore/static/feeds/google/google_feed_ad_prods.csv'
	cfile = '/home/artevenue/website/estore/static/feeds/non_gallery_creatives.csv'
	domus_input = '/home/artevenue/website/estore/static/feeds/domus/domus_input.csv'
	domus_feed = '/home/artevenue/website/estore/static/feeds/domus/domus_feed.csv'

	wa_input = '/home/artevenue/website/estore/static/feeds/wishaffair/wa_input.csv'
	wa_feed = '/home/artevenue/website/estore/static/feeds/wishaffair/wa_feed.csv'
	wa_prod_not_found = '/home/artevenue/website/estore/static/feeds/wishaffair/wa_prod_not_found.csv'
	wa_img_loc = '/home/artevenue/website/estore/static/feeds/wa/images/'

	tli_input = '/home/artevenue/website/estore/static/feeds/tli/tli_input.csv'
	tli_feed = '/home/artevenue/website/estore/static/feeds/tli/tli_feed.csv'
	tli_prod_not_found = '/home/artevenue/website/estore/static/feeds/tli/tli_prod_not_found.csv'
	tli_img_loc = '/home/artevenue/website/estore/static/feeds/tli/images/'


	hoo_input = '/home/artevenue/website/estore/static/feeds/hoo/hoo_input14Apr2021.csv'
	hoo_feed = '/home/artevenue/website/estore/static/feeds/hoo/hoo_feed.csv'
	hoo_prod_not_found = '/home/artevenue/website/estore/static/feeds/hoo/hoo_prod_not_found.csv'
	hoo_img_loc = '/home/artevenue/website/estore/static/feeds/hoo/images/'


	
else:
	fb_file_nm = 'facebook_feed_all_prods.csv'
	fb_ad_file_nm = 'facebook_feed_ad_prods.csv'
	fb_ad_in = 'fb_ad_prods_input.csv'
	google_file_nm = 'google_feed_all_prods.csv'
	google_ad_file_nm = 'google_feed_ad_prods.csv'
	cfile = 'c:/artevenue/PRODUCT_FEEDS/non_gallery_creatives.csv'
	domus_input = 'c:/artevenue/PRODUCT_FEEDS/domus/domus_input.csv'
	domus_feed = 'c:/artevenue/PRODUCT_FEEDS/domus/domus_feed.csv'

	wa_input = 'c:/artevenue/PRODUCT_FEEDS/wishaffair/wa_input.csv'
	wa_feed = 'c:/artevenue/PRODUCT_FEEDS/wishaffair/wa_feed.csv'
	wa_prod_not_found = 'c:/artevenue/PRODUCT_FEEDS/wishaffair/wa_prod_not_found.csv'
	wa_img_loc = 'c:/artevenue/PRODUCT_FEEDS/wishaffair/images/'

	tli_input = 'c:/artevenue/PRODUCT_FEEDS/tli/tli_input.csv'
	tli_feed = 'c:/artevenue/PRODUCT_FEEDS/tli/tli_feed.csv'
	tli_prod_not_found = 'c:/artevenue/PRODUCT_FEEDS/tli/tli_prod_not_found.csv'
	tli_img_loc = 'c:/artevenue/PRODUCT_FEEDS/tli/images/'

	hoo_input = 'c:/artevenue/PRODUCT_FEEDS/hoo/hoo_input14Apr2021.csv'
	hoo_feed = 'c:/artevenue/PRODUCT_FEEDS/hoo/hoo_feed.csv'
	hoo_prod_not_found = 'c:/artevenue/PRODUCT_FEEDS/hoo/hoo_prod_not_found.csv'
	hoo_img_loc = 'c:/artevenue/PRODUCT_FEEDS/hoo/images/'

def generate_all_prod_feed():

	## Collect all prod ids for non-gallery products with creatives
	non_g_prods = []
	with open(cfile) as nfile:
		non_g = csv.reader(nfile, delimiter=',')
		for n in non_g:
			non_g_prods.append(n[0])
			
	## Collect all prod ids that are be used to AD display in FB
	fb_prod_for_ad = []
	with open(fb_ad_in) as afile:
		fb_a = csv.reader(afile, delimiter=',')
		for n in fb_a:
			fb_prod_for_ad.append(n[0])
	
	with open(fb_file_nm, 'w', newline='') as fb_file, open(google_file_nm, 'w', newline='') as google_file, open(cfile) as ngal_file, open(fb_ad_file_nm, 'w', newline='') as fb_ad_file, open(google_ad_file_nm, 'w', newline='') as google_ad_file:
		wr_fb = csv.writer(fb_file, quoting=csv.QUOTE_ALL)
		wr_fb_ad = csv.writer(fb_ad_file, quoting=csv.QUOTE_ALL)
		wr_google = csv.writer(google_file, quoting=csv.QUOTE_ALL)
		wr_google_ad = csv.writer(google_ad_file, quoting=csv.QUOTE_ALL)
		row_fb =['id', 'title', 'description', 'availability', 'condition',
			'price', 'link', 'image_link', 'brand', 'additional_image_link',
			'age_group', 'color', 'gender', 'item_group_id', 'google_product_category',
			'material', 'pattern', 'product_type', 'sale_price', 'sale_price_effective_date',
			'shipping', 'shipping_weight', 'size', 'custom_label_0', 'custom_label_1',
			'custom_label_2', 'custom_label_3', 'custom_label_4']					
		wr_fb.writerow(row_fb)
		wr_fb_ad.writerow(row_fb)
		
		row_google =['id', 'title', 'description', 'link', 'condition',
			'price', 'availability', 'image_link', 'mpn', 'brand', 
			'google product category', 'product type', 'custom_label_0', 'custom_label_1',
			'custom_label_2', 'custom_label_3', 'custom_label_4']			
		wr_google.writerow(row_google)
		wr_google_ad.writerow(row_google)

		non_gallery = csv.reader(ngal_file, delimiter=',')		

		curated = Curated_collection.objects.all()
		gallery = Gallery.objects.filter(is_published=True)

		##products = Stock_image.objects.filter(is_published = True)
		print("processing...." + str(curated.count()))
		cnt = 0

		for c in curated:
			p = c.product
			## Skip non-gallery prods that have creative
			if p.product_id in non_g_prods:
				print("skipping " + str(p.product_id))
				continue
			
			if p.is_published == False:
				print("skipping " + str(p.product_id) + ", it is not published.")
				continue				
			
			cnt = cnt + 1
			print(str(cnt) + "....")
			
			#image_width = 10
			#image_height = 10
			#if p.orientation == 'Vertical' or p.orientation == 'Square':
			#	image_width = 10
			#	image_height = round(image_width / p.aspect_ratio)
			#else:
			#	image_height = 10
			#	image_width = round(image_height * p.aspect_ratio)			
			
			## Standard sizes
			if p.aspect_ratio > 1:
				image_height = 8
				image_width = round(image_height * p.aspect_ratio)
			else:
				image_width = 10
				image_height = round(image_width / p.aspect_ratio)

			if p.artist == 'Huynh, Duy':
				if p.aspect_ratio > 1:
					image_height = 16
					image_width = round(image_height * p.aspect_ratio)
				else:
					image_width = 16
					image_height = round(image_width / p.aspect_ratio)

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
			mount_size = 1

			## Set moulding and mount size based on the standard size
			mount_size = 1 if image_width <= 24 else 2 if image_width <= 42 else 3
			moulding_id = 18 if image_width <= 24 else 24
			
			#####################################################
			## With frame PAPER
			#####################################################
			#         Get the item price
			price = get_prod_price(p.product_id, 
					prod_type= p.product_type_id,
					image_width=image_width, 
					image_height=image_height,
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
			if item_price == 0 or item_price is None:				
				err_flg = True
				print( 'Price not available for this image ' + str(p.product_id) )
				continue
			# END:	if item price not found, don't add to cart

			## Increase price by 25%, to manage the returns			##################################################
			##item_price = item_price + round((item_price*20/100))

			#	Calculate sub total, tax for the item
			item_tax = 0
			item_sub_total = 0
			#### Get Tax
			taxes = get_taxes()
			if p.product_type_id == 'STOCK-IMAGE':
				tax_rate = taxes['stock_image_tax_rate']
			if p.product_type_id == 'ORIGINAL-ART':
				tax_rate = taxes['original_art_tax_rate']
			if p.product_type_id == 'USER-IMAGE':
				tax_rate = taxes['user_image_tax_rate']
			if p.product_type_id == 'STOCK-COLLAGE':
				tax_rate = taxes['stock_image_tax_rate']
			if p.product_type_id == 'FRAME':
				tax_rate = taxes['frame_tax_rate']

			quantity = 1

			# Calculate tax and sub_total
			item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
			item_tax = round( (item_price*quantity) - item_sub_total )
			#	END: Calculate sub total, tax for the item

			desc = "Make your interiors awesome with our top quality artworks. Complete customization available online. Licensed art print. Largest collection in India Top quality with affordable prices. 15% discount on 1st order when you sign up. Free shipping. Satisfaction guaranteed."
			title = "Wall Art: " + p.name + ", By: " + p.artist	

			## Get product category
			cat = Stock_image_stock_image_category.objects.filter(
				stock_image = p).first()

			#######################################
			# Check if this prod has a creative        ###
			# If it has skip, it will added at the end ###
			#######################################
			img_link = 'https://artevenue.com/static/' + p.url
				
			#for n in non_gallery:
			#	if p.product_id == n[0]:
			#		img_link = n[1]
			#		print("Creative file found for " + str(n[0]))

			custom_label0 = ''
			custom_label1 = ''
			custom_label2 = ''
			
			for f in fb_prod_for_ad:
				if str(p.product_id) == f:
					custom_label2 = 'AD'
					print('AD Prod: ' + f )
			

			row_fb = [p.product_id, title[:140], desc, 'in stock', 'new', item_price, 
			'https://artevenue.com/art-print/' + str(p.product_id) + '/', 
			img_link, 
			"Arte'Venue", '', '', '', '', '', 
			'Home & Garden > Decor > Artwork', '', '', 
			cat.stock_image_category.name.title(), '', '', 'Free Shipping', '', 
			str(image_width + 4) + " X " + str(image_height + 4) + " inch" , 
			'', '', custom_label2, '', '']
						
			wr_fb.writerow(row_fb)

			row_google = [p.product_id, title[:140], desc, 
			'https://artevenue.com/art-print/' + str(p.product_id) + '/',
			'new', str(item_price) + ' INR', 'in stock', 
			img_link, 
			p.part_number, "Arte'Venue", '500044', 
			cat.stock_image_category.name.title(), '', '', custom_label2, '', ''
			]
			# 'paintings > paintings online > wall art > paintings for home > paintings for living room > paintings for bedroom'
			
			wr_google.writerow(row_google)
			
		####### GALLERY WALLS ###########
		for g in gallery:
			cnt = cnt + 1
			print(str(cnt) + "....")

			### GET GALLER WALL PRICE
			gallery_variation = Gallery_variation.objects.filter(gallery_id = g.gallery_id, is_parent = True).first()
			gallery_items = Gallery_item.objects.filter(gallery_id = g.gallery_id, 
				gallery_variation = gallery_variation)
			gallery_items = gallery_items.values(
					'item_id', 'gallery_id', 'gallery_variation_id', 'product_id', 'product_name', 'product_type_id',
					'moulding_id', 'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id',
					'mount__name', 'mount__color', 'mount_size', 'board_id', 'acrylic_id', 'stretch_id', 'image_width', 
					'image_height', 'moulding__width_inner_inches')

			gallery_variation_price = 0	
			for gal_item in gallery_items:
				item_price = get_variation_item_price(gal_item['item_id'])
				gallery_variation_price = gallery_variation_price + item_price
			###############
						
			row_fb = ['G' + str(g.gallery_id), 'Gallery Wall Set: ' + g.title, 
			"Designer curated, well styled gallery wall. A set of " + str(g.set_of) +  " artworks. Make your interiors awesome with our exquisite and largest art collection in India. Top quality products and satisfaction guarantee.", 
			'in stock', 'new', gallery_variation_price, 
			'https://artevenue.com/gallery-wall/' + str(g.gallery_id) + '/', 
			'https://artevenue.com/static/' + g.room_view_url, 
			"Arte'Venue", '', '', '', '', '', 
			'Home & Garden > Decor > Artwork', '', '', 
			g.key_words.title(), '', '', 'Free Shipping', '', 
			str(gallery_variation.wall_area_width) + " X " + str(gallery_variation.wall_area_height) + " inch" + 
			'', '', '', '', '']
						
			wr_fb.writerow(row_fb)
			wr_fb_ad.writerow(row_fb)			

			row_google = ['G' + str(g.gallery_id), 'Gallery Wall Set: ' + g.title,  
			"Designer curated, well styled gallery wall. A set of " + str(g.set_of) +  " artworks. Make your interiors awesome with our exquisite and largest art collection in India. Top quality products and satisfaction guarantee.", 
			'https://artevenue.com/gallery-wall/' + str(g.gallery_id) + '/',
			'new', str(gallery_variation_price) + ' INR', 'in stock', 
			'https://artevenue.com/static/' + g.room_view_url, 
			'', "Arte'Venue", '500044', 
			'gallery walls > paintings > paintings online > wall art > paintings for home > paintings for living room > paintings for bedroom'
			]
						
			wr_google.writerow(row_google)
			wr_google_ad.writerow(row_google)

		##############################################
		## Include all products that have creatives ##
		## but not already included in the feed     ##
		##############################################
		ids = curated.values('product_id')
		for n in non_gallery:
			if n[0] not in ids:
				prod = Product_view.objects.filter(product_id = n[0]).first()
				if prod:

					#image_width = 10
					#image_height = 10
					#if prod.orientation == 'Vertical' or prod.orientation == 'Square':
					#	image_width = 10
					#	image_height = round(image_width / prod.aspect_ratio)
					#else:
					#	image_height = 10
					#	image_width = round(image_height * prod.aspect_ratio)			

					## Standard sizes
					if prod.aspect_ratio > 1:
						image_height = 8
						image_width = round(image_height * prod.aspect_ratio)
					else:
						image_width = 10
						image_height = round(image_width / prod.aspect_ratio)


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
					mount_size = 1
					
					## Set moulding and mount size based on the standard size
					mount_size = 1 if image_width <= 24 else 2 if image_width <= 42 else 3
					moulding_id = 18 if image_width <= 24 else 24


					#####################################################
					## With frame PAPER
					#####################################################
					#         Get the item price
					price = get_prod_price(prod.product_id, 
							prod_type= prod.product_type_id,
							image_width=image_width, 
							image_height=image_height,
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
					if item_price == 0 or item_price is None:				
						err_flg = True
						print( 'Price not available for this image ' + str(prod.product_id) )
						continue
					# END:	if item price not found, don't add to cart
							
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
					
					quantity = 1
					
					# Calculate tax and sub_total
					item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
					item_tax = round( (item_price*quantity) - item_sub_total )
					#	END: Calculate sub total, tax for the item

					desc = "Make your interiors awesome with our top quality artworks. Complete customization available online. Licensed art print. Largest collection in India Top quality with affordable prices. 15% discount on 1st order when you sign uprod. Free shipping. Satisfaction guaranteed."
					title = "Wall Art: " + prod.name + ", By: " + prod.artist

					## Get product category			
					cat = Stock_image_stock_image_category.objects.filter(
						stock_image = prod.product_id).first()

					row_fb = [prod.product_id, title[:140], desc, 'in stock', 'new', item_price, 
					'https://artevenue.com/art-print/' + str(prod.product_id) + '/', 
					n[1], 
					"Arte'Venue", '', '', '', '', '', 
					'Home & Garden > Decor > Artwork', '', '', 
					cat.stock_image_category.name.title(), '', '', 'Free Shipping', '', 
					str(image_width + 4) + " X " + str(image_height + 4) + " inch" + 
					'', '', '', '', '']

					wr_fb.writerow(row_fb)
					wr_fb_ad.writerow(row_fb)

					row_google = [prod.product_id, title[:140], desc, 
					'https://artevenue.com/art-print/' + str(prod.product_id) + '/',
					'new', str(item_price) + ' INR', 'in stock', 
					n[1], 
					prod.part_number, "Arte'Venue", '500044', 
					'paintings > paintings online > wall art > paintings for home > paintings for living room > paintings for bedroom'
					]

					wr_google.writerow(row_google)
					wr_google_ad.writerow(row_google)


def generate_domus_feed():
	##################################
	# DOMUS FEED GENERATION
	##################################
	print(domus_input)
	cfile = Path(domus_input)
	if not cfile.is_file():
		print("domus_input.csv file did not found")
		return

	file = open(domus_input)	
	cr = csv.reader(file, delimiter=',')

	with open(domus_feed, 'w', newline='') as domus_file:
		wr_domus = csv.writer(domus_file, quoting=csv.QUOTE_ALL)	
		row_d = ['Model Number', 'Brand', 'Category Name', 'Sub Category Name', 'Style', 
				'Product Name', 'Description', 'MRP', 'Cost (Incl GST)', 'URL',
				'Product Width (inch)', 'Product Height (inch)', 'Product Breadth (inch)', 
				'Packed Box Weight (KG)',
				'Packed Box Width (inch)', 'Packed Box Height (inch)', 'Packed Box Breath (inch)', 
				'HSN','GST%']

		wr_domus.writerow(row_d)

		cnt = 0
		for row in cr:
			if cnt == 0:
				cnt = cnt+1
				continue
			
			cnt = cnt+1
			product_type_id = row[10]
			image_width = row[2]
			image_height = row[3]
			print_medium_id = row[4]
			acr_id = row[8]
			mld_id = row[5]
			mnt_size = row[7]
			mnt_id = row[6]
			brd_id = row[9]
			str_id = row[11]
			product_id = row[1]
			print("Processing...." + product_id)

			p = Stock_image.objects.filter(product_id = product_id).first()
			
			if not p:
				print("Product " + product_id + " not found, skipped...")

			#####################################################
			## Get Price
			#####################################################
			#         Get the item price
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
			if item_price == 0 or item_price is None:				
				err_flg = True
				print( 'Price not available for this image ' + str(p.product_id) )
				continue
			# END:	if item price not found, don't add to cart

			## MRP price (+ 20% )
			mrp = item_price + round((item_price*20/100))
			
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
			
			quantity = 1000
			
			# Calculate tax and sub_total
			item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
			item_tax = round( (item_price*quantity) - item_sub_total )
			#	END: Calculate sub total, tax for the item

			desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

			## Get product category			
			cat = Stock_image_stock_image_category.objects.filter(
				stock_image_id = product_id).first()

			if mld_id:
				moulding = Moulding.objects.filter(moulding_id = mld_id).first()
				title = p.name + ", By: " + p.artist
			else:
				moulding = None
				title = p.name + ", By: " + p.artist
				
			if mnt_id:
				mount = Mount.objects.filter(mount_id = mnt_id).first()
			else:
				mount = None
				
			length = int(image_height)
			if mld_id:
				if moulding.width_inner_inches:
					length = formatNumber(length + (moulding.width_inner_inches * 2))
				if mnt_id:
					if mnt_size:
						length = formatNumber(length + (int(mnt_size) * 2))
			
			width = int(image_width)
			if mld_id:
				if moulding.width_inner_inches:
					width = formatNumber(width + (moulding.width_inner_inches * 2))
				if mnt_id:
					if mnt_size:
						width = formatNumber(width + (int(mnt_size) * 2))								

			if str_id:
				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; \n" + cat.stock_image_category.name.title() + " Painting on Stretched Canvas; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
			else:
				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; \n" + cat.stock_image_category.name.title() + " Painting with frame; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
			
			if moulding:
				prod_details = prod_details + "Premium quality artwork, Print produced using fine art reproduction printer, Top quality frame with classy finish; \n"
			else:
				prod_details = prod_details + "Premium quality artwork, Print produced using fine art reproduction printer; \n"
				
			
			prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

			#if print_medium_id == 'PAPER':
			#	prod_details = prod_details + "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
			#else:
			#	prod_details = prod_details + "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \n"
			
			t_size = ''
			if mld_id:
				prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
			if mnt_id:
				prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
			
			if mount:
				prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"


			if str_id:
				prod_details = prod_details + "Canvas wrapped over frame at the back;\n"
			
			prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
			
			## Total Size
			t_size_width = int(image_width)
			t_size_height = int(image_height)
			if mld_id:
				if moulding.width_inner_inches:
					t_size_width = t_size_width + moulding.width_inner_inches *2
					t_size_height = t_size_height + moulding.width_inner_inches *2
			if mnt_id:
				t_size_width = t_size_width + int(mnt_size)*2
				t_size_height = t_size_height + int(mnt_size)*2
			
			t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
			prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

			t_s = t_size_width * t_size_height
			if t_s <= 256:
				ship_weight = 1.5
			elif t_s <= 576:
				ship_weight = 2
			elif t_s <= 900:
				ship_weight = 2.5
			elif t_s <= 1600:
				ship_weight = 3
			else:
				ship_weight = 3.5				

			row_d = [str(product_id) + "-" + str(image_width), "Arte'Venue", 
					'PAINTING', cat.stock_image_category.name.title(), 'Wall Hanging', 
					title, prod_details, mrp, item_price, row[12],
				t_size_width, t_size_height, 2, ship_weight,
				t_size_width + 3, t_size_height + 3, 5, '97020000',
				tax_rate]

			wr_domus.writerow(row_d)
			
def generate_wa_feed():
	##################################
	# WishAffair FEED GENERATION
	##################################
	cfile = Path(wa_input)
	if not cfile.is_file():
		print("wa_input.csv file not found")
		return

	file = open(wa_input)	
	cr = csv.reader(file, delimiter=',')

	with open(wa_feed, 'w', newline='') as wa_file:
		wr_wa = csv.writer(wa_file, quoting=csv.QUOTE_ALL)	
		row_d = ['Name of Product', 'Model Number', 'Base Price', 'GST', 'MRP', 
				'Description', 'dimensions', 'Available Quality', 'Approximate Weight in Kg', 
				'Color', 'Images', 'Material', 'Care Instructions', 'Any Other Info']

		wr_wa.writerow(row_d)

		cnt = 0
		for row in cr:
			if cnt == 0:
				cnt = cnt+1
				continue
			
			cnt = cnt+1
			product_type_id = row[11]
			image_width = row[4]
			image_height = row[5]
			print_medium_id = row[10]
			acr_id = row[6]
			mld_id = row[8]
			mnt_size = row[3]
			mnt_id = row[9]
			brd_id = row[7]
			str_id = row[12]
			product_id = row[0]
			g_size = row[13] 
			g_price = row[14]
			gallery_id = row[15]
			g_variation_id = row[16]

			print("Processing...." + product_id)

			if product_type_id == 'STOCK-IMAGE':
				p = Stock_image.objects.filter(product_id = product_id).first()
				
				if not p:
					print("Product " + product_id + " not found, skipped...")

				#####################################################
				## Get Price
				#####################################################
				#         Get the item price
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

				## MRP price (+ 20% )
				##mrp = item_price + round((item_price*20/100))
				
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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				## Get product category			
				cat = Stock_image_stock_image_category.objects.filter(
					stock_image_id = product_id).first()

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				if str_id:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "\nPrint Surface: " + print_medium_id.title() + ". \n"
				else:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "\nPrint Surface: " + print_medium_id.title() + ". \n"

				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = t_size_width + moulding.width_inner_inches *2
						t_size_height = t_size_height + moulding.width_inner_inches *2
				if mnt_id:
					t_size_width = t_size_width + int(mnt_size)*2
					t_size_height = t_size_height + int(mnt_size)*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + ". "

				
				if moulding:
					prod_details = prod_details + "\nPremium quality artwork, Print produced using fine art reproduction printer, Top quality frame with classy finish. \n"
				else:
					prod_details = prod_details + "\nPremium quality artwork, Print produced using fine art reproduction printer. \n"
					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + ". \n"

				#if print_medium_id == 'PAPER':
				#	prod_details = prod_details + "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
				#else:
				#	prod_details = prod_details + "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \n"
				
				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + ". \n"
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility. \n"
				
				prod_details = prod_details + "Comes with hooks and is ready for hanging."				

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				#['Name of Product', 'Model Number', 'Base Price', 'GST', 'MRP', 
				#	'Description', 'dimensions', 'Available Quality', 'Approximate Weight in Kg', 
				#	'Color', 'Images', 'Material', 'Care Instructions', 'Any Other Info']


				row_d = [ title, str(product_id), item_sub_total, item_tax, item_price,
					prod_details, t_size, 1000, ship_weight, 'N/A', row[2], 'N/A', 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.']
				
				wr_wa.writerow(row_d)
			'''
			elif product_type_id == 'GALLERY-WALL':
				
				gallery_item = Gallery_item.objects.filter(gallery_id = gallery_id, gallery_variation_id = g_variation_id)
				
				item_sub_total
				item_tax
				
				prod_details = gallery_item.gallery.title + ': A set containing ' + str(gallery_item.gallery.set_of) 
					+ ' artworks.'
					
				cnt = 0
				for gi in gallery_items
				
					p = Product_views.objects.filter(product_id = gi.product_id, product_type_id = product_type_id)
					if p:
						cnt = cnt+1						
						prod_details = prod_details + 'Artwork 1: ' + p.name + " size: 
						ship_weight
				
				row_d = [ 'Gallery Wall Set: ' + gallery_item.gallery.title, str(product_id), 
					item_sub_total, item_tax, g_price,
					prod_details, g_size, 1000, ship_weight, 'N/A', row[2], 'N/A', 
					'Wipe with clean, soft, and dry cloth', 
					'Designer curated gallery wall set. Ships in 2-3 days']
				
				wr_wa.writerow(row_d)
			'''


def generate_tli_feed():
	##################################
	# TLI FEED GENERATION
	##################################
	cfile = Path(tli_input)
	if not cfile.is_file():
		print("tli_input.csv file not found")
		return

	file = open(tli_input)	
	cr = csv.reader(file, delimiter=',')

	with open(tli_feed, 'w', newline='') as tli_file, open(tli_prod_not_found, 'w', newline='') as notfound_file:
	
		wr_tli = csv.writer(tli_file, quoting=csv.QUOTE_ALL)	
		wr_nf = csv.writer(notfound_file, quoting=csv.QUOTE_ALL)	

		row_d = ["Title", "Product ID", "Print Surface", "Image Size", 
				"Frame", "Product_details", "Product Size",
				"Sub Total", "Tax", "Total Price", "Quantity", "Shipping Weight",
				"Care Instructions", "Shipping Timeline"]						

		wr_tli.writerow(row_d)
		type_a = ["14X16", "18X22", "22X26", "28X32"]
		type_b = ["18X18", "22X22", "37X37", "43X43"]
		type_c = ["18X15", "28X23", "37X31", "43X35"]

		row_nf = ["Product ID", "Remarks"]
		wr_nf.writerow(row_nf)
		
		cnt = 0
		for row in cr:
			if cnt == 0:
				cnt = cnt+1
				continue
			
			cnt = cnt+1
			product_id = row[1]
			type = row[2]
			print("Processing...." + product_id)
			if not product_id:
				print("Product id not found, skipped...")
				wr_nf.writerow([row[1], "Product not found"])
				continue
			
			p = Stock_image.objects.filter(product_id = product_id).first()				
			if not p:
				print("Product " + product_id + " not found, skipped...")
				wr_nf.writerow([row[1], "Product not found"])
				continue
				
			if p.is_published == False:
				print("Product " + product_id + " not found, skipped...")
				wr_nf.writerow([row[1], "Product is unpublished"])
				continue
			
			if type == 'A':
				t_sizes = type_a
			elif type == 'B':
				t_sizes = type_b
			elif type == 'C':
				t_sizes = type_c
			else:
				print("Product " + product_id + " wrong TYPE, skipped...")
				wr_nf.writerow([row[1], "Wrong Size"])
				continue
				
			product_type_id = 'STOCK-IMAGE'
			for s in t_sizes:
				total_size = s.split("X")
				t_w = int(total_size[0])
				#t_h = int(total_size[1]) - 4
				t_h = int(total_size[1])
				
				################################################################################
				################################################################################
				##      SURFACE: PAPER
				################################################################################
				################################################################################


				###################################################
				############# WITHOUT FRAME
				image_width = str(t_w  - 4 )
				image_height = str(round(int(image_width)/p.aspect_ratio))
				
				mld_id = None
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = None				
				print_medium_id = 'PAPER'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = t_size_width + moulding.width_inner_inches *2
						t_size_height = t_size_height + moulding.width_inner_inches *2
				if mnt_id:
					t_size_width = t_size_width + int(mnt_size)*2
					t_size_height = t_size_height + int(mnt_size)*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (without frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, t_size,
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.']
				
				wr_tli.writerow(row_d)
				
				##########################################################
				############ Black Frame
				total_size = s.split("X")				
				t_w = int(total_size[0])
				t_h = int(total_size[1])

				image_width = str(t_w - 4 )
				image_height = str(round(int(image_width) / p.aspect_ratio))
				
				mld_id = '18'
				mnt_id = '3'
				mnt_size = '1'
				acr_id = '1'
				brd_id = '1'
				str_id = None				
				print_medium_id = 'PAPER'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = t_size_width + moulding.width_inner_inches *2
						t_size_height = t_size_height + moulding.width_inner_inches *2
				if mnt_id:
					t_size_width = t_size_width + int(mnt_size)*2
					t_size_height = t_size_height + int(mnt_size)*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, t_size,
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.']
				
				wr_tli.writerow(row_d)


				###################################################
				###### White Frame ################################
				#total_size = s.split("X")
				#t_w = int(total_size[0])
				#t_h = int(image_height) + 4

				#image_width = str(t_w - 4)
				#image_height = str(round(int(image_width) / p.aspect_ratio))

				mld_id = '8'
				mnt_id = '3'
				mnt_size = '1'
				acr_id = '1'
				brd_id = '1'
				str_id = None				
				print_medium_id = 'PAPER'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = t_size_width + moulding.width_inner_inches *2
						t_size_height = t_size_height + moulding.width_inner_inches *2
				if mnt_id:
					t_size_width = t_size_width + int(mnt_size)*2
					t_size_height = t_size_height + int(mnt_size)*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, t_size,
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.']
				
				wr_tli.writerow(row_d)


				################################################################################
				################################################################################
				##      SURFACE: CANVAS
				################################################################################
				################################################################################

				
				#######################################################
				############# WITHOUT FRAME
				total_size = s.split("X")
				t_w = int(total_size[0])
				t_h = int(total_size[1])

				image_width = str(t_w  - 2 )
				image_height = str(round(int(image_width) / p.aspect_ratio))
								
				mld_id = None
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = None				
				print_medium_id = 'CANVAS'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = t_size_width + moulding.width_inner_inches *2
						t_size_height = t_size_height + moulding.width_inner_inches *2
				if mnt_id:
					t_size_width = t_size_width + int(mnt_size)*2
					t_size_height = t_size_height + int(mnt_size)*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (without frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, t_size,
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.']
				
				wr_tli.writerow(row_d)


				##################################################
				## Black frame
				total_size = s.split("X")
				t_w = int(total_size[0])
				t_h = int(total_size[1])
				#t_h = round(t_w / p.aspect_ratio)
				
				image_width = str(t_w - 2)
				image_height = str(round(int(image_width) / p.aspect_ratio))

				mld_id = '27'
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = '1'
				print_medium_id = 'CANVAS'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				## Get product category			
				cat = Stock_image_stock_image_category.objects.filter(
					stock_image_id = product_id).first()

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				if str_id:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				else:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = t_size_width + moulding.width_inner_inches *2
						t_size_height = t_size_height + moulding.width_inner_inches *2
				if mnt_id:
					t_size_width = t_size_width + int(mnt_size)*2
					t_size_height = t_size_height + int(mnt_size)*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, t_size,
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.']
				
				wr_tli.writerow(row_d)

				##################################################
				## White frame
				#total_size = s.split("X")
				#t_w = int(total_size[0])
				#t_h = int(image_height) + 2
				#t_h = round(t_w / p.aspect_ratio)

				#image_width = str(t_w - 2)
				#image_height = str(round(int(image_width) / p.aspect_ratio))
				
				mld_id = '28'
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = '1'
				print_medium_id = 'CANVAS'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				## Get product category			
				cat = Stock_image_stock_image_category.objects.filter(
					stock_image_id = product_id).first()

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				if str_id:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				else:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + ", made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = t_size_width + moulding.width_inner_inches *2
						t_size_height = t_size_height + moulding.width_inner_inches *2
				if mnt_id:
					t_size_width = t_size_width + int(mnt_size)*2
					t_size_height = t_size_height + int(mnt_size)*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, t_size,
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.']
				
				wr_tli.writerow(row_d)



def generate_hoo_feed(partner_code='HOO'):
	
	i_file = hoo_input
	i_feed = hoo_feed
	prod_not_found = hoo_prod_not_found

	type_a = ["13X16", "16X21", "20X26", "26X34"]
	type_b = ''
	type_c = ''
	
	img_loc = hoo_img_loc

		
	##################################
	# PARTNER FEED GENERATION
	##################################
	cfile = Path(i_file)
	if not cfile.is_file():
		print(i_file + " file not found")
		return

	file = open(i_file)	
	cr = csv.reader(file, delimiter=',')

	from django.http import HttpRequest
	request = HttpRequest()
	request.method = 'GET'

	with open(i_feed, 'w', newline='') as i_file, open(prod_not_found, 'w', newline='') as notfound_file:
	
		wr_partner = csv.writer(i_file, quoting=csv.QUOTE_ALL)	
		wr_nf = csv.writer(notfound_file, quoting=csv.QUOTE_ALL)	

		row_d = ["Title", "Product ID", "Print Surface", "Image Size", 
				"Frame", "Product_details", "Product Size",
				"Sub Total", "Tax", "Total Price", "Quantity", "Shipping Weight",
				"Care Instructions", "Shipping Timeline", "Product Image"]						

		wr_partner.writerow(row_d)

		row_nf = ["Product ID", "Remarks"]
		wr_nf.writerow(row_nf)
		
		creative_url = 'https://artevenue.com/static/feeds/amazon/creatives/'
		
		cnt = 0
		for row in cr:
			if cnt == 0:
				cnt = cnt+1
				continue
			
			cnt = cnt+1
			product_id = row[0]
			creative_img = row[1]
			type = row[2]
			print("Processing...." + product_id)
			if not product_id:
				print("Product id not found, skipped...")
				wr_nf.writerow([row[0], "Product not found"])
				continue
			
			p = Stock_image.objects.filter(product_id = product_id).first()				
			if not p:
				print("Product " + product_id + " not found, skipped...")
				wr_nf.writerow([row[0], "Product not found"])
				continue
				
			if p.is_published == False:
				print("Product " + product_id + " not found, skipped...")
				wr_nf.writerow([row[0], "Product is unpublished"])
				continue
			
			if p.aspect_ratio < 1:
				t_sizes = type_a
			elif p.aspect_ratio == 1:
				t_sizes = type_b
			else:
				t_sizes = type_c
				
			product_type_id = 'STOCK-IMAGE'
			for s in t_sizes:
				total_size = s.split("X")
				t_w = int(total_size[0])
				#t_h = int(total_size[1]) - 4
				t_h = int(total_size[1])
				
				################################################################################
				################################################################################
				##      SURFACE: PAPER
				################################################################################
				################################################################################


				###################################################
				############# WITHOUT FRAME
				image_width = str(t_w  - 5 )
				image_height = str(round(int(image_width)/p.aspect_ratio))				
				
				mld_id = None
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = None				
				print_medium_id = 'PAPER'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = round(t_size_width + moulding.width_inner_inches *2)
						t_size_height = round(t_size_height + moulding.width_inner_inches *2)
				if mnt_id:
					t_size_width = round(t_size_width + int(mnt_size)*2)
					t_size_height = round(t_size_height + int(mnt_size)*2)
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (without frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				#img_link = 'https://artevenue.com/static/' + p.url
				img_link = creative_img

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, total_size[0] + '" X' + total_size[1] + '" inch',
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.',
					img_link]
				
				wr_partner.writerow(row_d)
				
				##########################################################
				############ Black Frame
				total_size = s.split("X")				
				t_w = int(total_size[0])
				t_h = int(total_size[1])

				image_width = str(t_w - 5 )
				image_height = str(round(int(image_width) / p.aspect_ratio))
				
				mld_id = '26'
				mnt_id = '3'
				mnt_size = '2'
				acr_id = '1'
				brd_id = '1'
				str_id = None				
				print_medium_id = 'PAPER'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = round(t_size_width + moulding.width_inner_inches *2)
						t_size_height =round( t_size_height + moulding.width_inner_inches *2)
				if mnt_id:
					t_size_width = round(t_size_width + int(mnt_size)*2)
					t_size_height = round(t_size_height + int(mnt_size)*2)				
					
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				## Get Image & Save
				#framed_img = get_FramedImage_by_id(request, product_id, mld_id, mount.color, 
				#	int(mnt_size), int(image_width), 'STOCK-IMAGE' )
				#img_nm = str(p.product_id) + '_' + image_width + '_pb.jpg'
				#framed_img.save(img_loc + img_nm)
				
				#img_link = 'https://artevenue.com/static/feeds/hoo/images/' + img_nm
				img_link = creative_img
				
				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, total_size[0] + '" X' + total_size[1] + '" inch',
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.',
					img_link]
				
				wr_partner.writerow(row_d)


				###################################################
				###### White Frame ################################
				#total_size = s.split("X")
				#t_w = int(total_size[0])
				#t_h = int(image_height) + 4

				#image_width = str(t_w - 4)
				#image_height = str(round(int(image_width) / p.aspect_ratio))

				mld_id = '20'
				mnt_id = '3'
				mnt_size = '2'
				acr_id = '1'
				brd_id = '1'
				str_id = None				
				print_medium_id = 'PAPER'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = round(t_size_width + moulding.width_inner_inches *2)
						t_size_height = round(t_size_height + moulding.width_inner_inches *2)
				if mnt_id:
					t_size_width = round(t_size_width + int(mnt_size)*2)
					t_size_height = round(t_size_height + int(mnt_size)*2)
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				## Get Image & Save
				#framed_img = get_FramedImage_by_id(request, product_id, mld_id, mount.color, 
				#	int(mnt_size), int(image_width), 'STOCK-IMAGE' )

				#img_nm = str(p.product_id) + '_' + image_width + '_pw.jpg'
				#framed_img.save(img_loc + img_nm)
				
				#img_link = 'https://artevenue.com/static/feeds/hoo/images/' + img_nm
				img_link = creative_img

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, total_size[0] + '" X' + total_size[1] + '" inch',
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.',
					img_link]
				
				wr_partner.writerow(row_d)


				################################################################################
				################################################################################
				##      SURFACE: CANVAS
				################################################################################
				################################################################################

				
				#######################################################
				############# WITHOUT FRAME
				total_size = s.split("X")
				t_w = int(total_size[0])
				t_h = int(total_size[1])

				image_width = str(t_w  - 2 )
				image_height = str(round(int(image_width) / p.aspect_ratio))
								
				mld_id = None
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = None				
				print_medium_id = 'CANVAS'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " +  "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = round(t_size_width + moulding.width_inner_inches *2)
						t_size_height = round(t_size_height + moulding.width_inner_inches *2)
				if mnt_id:
					t_size_width = round(t_size_width + int(mnt_size)*2)
					t_size_height = round(t_size_height + int(mnt_size)*2)
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (without frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				#img_link = 'https://artevenue.com/static/' + p.url
				img_link = creative_img

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details,  total_size[0] + '" X' + total_size[1] + '" inch',
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.',
					img_link]
				
				wr_partner.writerow(row_d)


				##################################################
				## Black frame
				total_size = s.split("X")
				t_w = int(total_size[0])
				t_h = int(total_size[1])
				#t_h = round(t_w / p.aspect_ratio)
				
				image_width = str(t_w - 2)
				image_height = str(round(int(image_width) / p.aspect_ratio))

				mld_id = '26'
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = '1'
				print_medium_id = 'CANVAS'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				## Get product category			
				cat = Stock_image_stock_image_category.objects.filter(
					stock_image_id = product_id).first()

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				if str_id:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				else:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + " (" + str(formatNumber(moulding.width_inches)) + " inch), made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = round(t_size_width + moulding.width_inner_inches *2)
						t_size_height = round(t_size_height + moulding.width_inner_inches *2)
				if mnt_id:
					t_size_width = round(t_size_width + int(mnt_size)*2)
					t_size_height = round(t_size_height + int(mnt_size)*2)
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				## Get Image & Save
				#framed_img = get_FramedImage_by_id(request, product_id, mld_id, '', 
				#	0, int(image_width), 'STOCK-IMAGE' )

				#img_nm = str(p.product_id) + '_' + image_width + '_cb.jpg'
				#framed_img.save(img_loc + img_nm)
				
				#img_link = 'https://artevenue.com/static/feeds/hoo/images/' + img_nm
				img_link = creative_img

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, total_size[0] + '" X' + total_size[1] + '" inch',
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.',
					img_link]
				
				wr_partner.writerow(row_d)

				##################################################
				## White frame
				#total_size = s.split("X")
				#t_w = int(total_size[0])
				#t_h = int(image_height) + 2
				#t_h = round(t_w / p.aspect_ratio)

				#image_width = str(t_w - 2)
				#image_height = str(round(int(image_width) / p.aspect_ratio))
				
				mld_id = '20'
				mnt_id = None
				mnt_size = None
				acr_id = None
				brd_id = None
				str_id = '1'
				print_medium_id = 'CANVAS'
				
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
				if item_price == 0 or item_price is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart

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
				item_sub_total = round( (item_price*quantity) / (1 + (tax_rate/100)), 2 )
				item_tax = round( (item_price*quantity) - item_sub_total )
				#	END: Calculate sub total, tax for the item

				desc = "Make your interiors awesome with premium quality artworks. Licensed art print. "			

				## Get product category			
				cat = Stock_image_stock_image_category.objects.filter(
					stock_image_id = product_id).first()

				if mld_id:
					moulding = Moulding.objects.filter(moulding_id = mld_id).first()
					title = p.name + ", By: " + p.artist
				else:
					moulding = None
					title = p.name + ", By: " + p.artist
					
				if mnt_id:
					mount = Mount.objects.filter(mount_id = mnt_id).first()
				else:
					mount = None
					
				length = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						length = formatNumber(length + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							length = formatNumber(length + (int(mnt_size) * 2))
				
				width = int(image_width)
				if mld_id:
					if moulding.width_inner_inches:
						width = formatNumber(width + (moulding.width_inner_inches * 2))
					if mnt_id:
						if mnt_size:
							width = formatNumber(width + (int(mnt_size) * 2))								

				if str_id:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				else:
					prod_details = "Title: " + p.name + ", Artist: " + p.artist + "; " + "\nPrinted on: " + print_medium_id.title() + "; \n"
				
				if moulding:
					prod_details = prod_details + "Top quality frame with classy finish; \n"					
				
				prod_details = prod_details + "Image Size: " + image_width + " X " + image_height + "; \n"

				t_size = ''
				if mld_id:
					prod_details = prod_details + "Frame: " + moulding.name + ", made of polystyrene, light weight, durable, premium finish. \n"
				if mnt_id:
					prod_details = prod_details + "Mount: " + mnt_size + " inch, Color: " + mount.name.lower() + "; \n"
				
				if mount:
					prod_details = prod_details + "Covered with acrylic glass for protection and clear visibility; \n"
				
				if mld_id:
					prod_details = prod_details + "Comes with hooks and is ready for hanging; \n"
				
				## Total Size
				t_size_width = int(image_width)
				t_size_height = int(image_height)
				if mld_id:
					if moulding.width_inner_inches:
						t_size_width = round(t_size_width + moulding.width_inner_inches *2)
						t_size_height = round(t_size_height + moulding.width_inner_inches *2)
				if mnt_id:
					t_size_width = round(t_size_width + int(mnt_size)*2)
					t_size_height = round(t_size_height + int(mnt_size)*2)
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): "  + t_size + "; "

				t_s = t_size_width * t_size_height
				if t_s <= 256:
					ship_weight = 1.5
				elif t_s <= 576:
					ship_weight = 2
				elif t_s <= 900:
					ship_weight = 2.5
				elif t_s <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5				

				## Get Image & Save
				#framed_img = get_FramedImage_by_id(request, product_id, mld_id, '', 
				#	0, int(image_width), 'STOCK-IMAGE' )

				#img_nm = str(p.product_id) + '_' + image_width + '_cw.jpg'
				#framed_img.save(img_loc + img_nm)
				
				
				#img_link = 'https://artevenue.com/static/feeds/hoo/images/' + img_nm
				img_link = creative_img

				row_d = [ title, str(product_id), print_medium_id, image_width + " X " + image_height + " inch",
					moulding.name if mld_id else 'None', prod_details, total_size[0] + '" X' + total_size[1] + '" inch',
					item_sub_total, item_tax, item_price,
					 1000, ship_weight, 
					'Wipe with clean, soft, and dry cloth', 
					'Ships by courier in 2-3 days. Usually deliveres in 3-10 days in most parts of India. It ususally takes between 4-7 days to deliver in all metro and major cities.',
					img_link]
				
				wr_partner.writerow(row_d)

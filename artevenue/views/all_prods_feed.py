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
	#fb_ad_in = '/home/artevenue/website/estore/static/feeds/facebook/fb_ad_prods_input.csv'
	google_file_nm = '/home/artevenue/website/estore/static/feeds/google/google_feed_all_prods.csv'
	#google_ad_file_nm = '/home/artevenue/website/estore/static/feeds/google/google_feed_ad_prods.csv'
	#cfile = '/home/artevenue/website/estore/static/feeds/non_gallery_creatives.csv'
	ad_prods_csv = '/home/artevenue/website/estore/static/feeds/ad_prods.csv'
	
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
	fb_file_nm = 'c:/artevenue/PRODUCT_FEEDS/facebook_feed_all_prods.csv'
	#fb_ad_file_nm = 'c:/artevenue/PRODUCT_FEEDS/facebook_feed_ad_prods.csv'
	#fb_ad_in = 'c:/artevenue/PRODUCT_FEEDS/fb_ad_prods_input.csv'
	google_file_nm = 'c:/artevenue/PRODUCT_FEEDS/google_feed_all_prods.csv'
	#google_ad_file_nm = 'c:/artevenue/PRODUCT_FEEDS/google_feed_ad_prods.csv'
	#cfile = 'c:/artevenue/PRODUCT_FEEDS/non_gallery_creatives.csv'
	ad_prods_csv = 'c:/artevenue/PRODUCT_FEEDS/ad_prods.csv'
	
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
	#non_g_prods = []
	#with open(cfile) as nfile:
	#	non_g = csv.reader(nfile, delimiter=',')
	#	for n in non_g:
	#		non_g_prods.append(n[0])
			
	## Collect all prod ids that are be used to AD display in FB
	#fb_prod_for_ad = []
	#with open(fb_ad_in) as afile:
	#	fb_a = csv.reader(afile, delimiter=',')
	#	for n in fb_a:
	#		fb_prod_for_ad.append(n[0])

	## Collect all prod ids that are be used for AD display
	ad_prods_singles = {}
	ad_prods_gw = {}
	ad_prods_sets = {}
	with open(ad_prods_csv) as afile:
		ad_p = csv.reader(afile, delimiter=',')
		for n in ad_p:
			if n[0] == 'SINGLES':				## Singles that are not part of set
				ad_prods_singles[n[1]]=n[2]
			if n[0] == 'GW':
				ad_prods_gw[n[1]]=n[2]
			if n[0] == 'SETS':					## Including singles as set
				ad_prods_sets[n[1]]=n[2]
	
	fb_prods = []
	with open(fb_file_nm) as f_file:
		fb_p = csv.reader(f_file, delimiter=',')
		for n in fb_p:
			fb_prods.append(n[0])

	google_prods = []
	with open(google_file_nm) as g_file:
		g_p = csv.reader(g_file, delimiter=',')
		for n in g_p:
			google_prods.append(n[0])

	############Product features, Images, Videos
	features_1 = "The best quality giclee prints produced at a very high resolution with full saturation and are fade resistant. Large format inkjet printers with archival inks are used to ensure consistent quality. Each artwork has an associated copyright and is licensed from the artist."
	features_2 = "Smooth finish matte, top-coated with an ink-receptive layer."				
	features_3 = "Frame is made of high density polystyrene which is moisture resistant, premium finish, durable and light weight."
	features_4 = "All artworks are ready to hang and come with necessary hooks."			
	video_1 = 'https://youtu.be/6vRss_YY48I'
	video_2 = 'https://youtu.be/vSrersiMjWk'
	product_highlight = "Fade-proof and high resolution giclee prints" + "," + "Best quality polystyrene frames" + "," + "Artist licensed artworks" + "," + "Premium quality" + "," + "Fully customizable"


	with open(fb_file_nm, 'w', newline='') as fb_file, open(google_file_nm, 'w', newline='') as google_file :
		#open(cfile) as ngal_file, open(fb_ad_file_nm, 'w', newline='') as fb_ad_file, open(google_ad_file_nm, 'w', newline='') as google_ad_file
		
		wr_fb = csv.writer(fb_file, quoting=csv.QUOTE_ALL)
		#wr_fb_ad = csv.writer(fb_ad_file, quoting=csv.QUOTE_ALL)
		wr_google = csv.writer(google_file, quoting=csv.QUOTE_ALL, delimiter='\t')
		#wr_google_ad = csv.writer(google_ad_file, quoting=csv.QUOTE_ALL)			
			
		row_fb =['id', 'title', 'description', 'availability', 'condition',
			'price', 'link', 'image_link', 'brand',
			'fb_product_category', 'quantity_to_sell_on_facebook', 'sale_price',
			'sale_price_effective_date', 'item_group_id', 'gender', 'color',
			'size', 'age_group',  'material', 'pattern', 'shipping', 'shipping_weight',
			'custom_label_0', 'custom_label_1',
			'custom_label_2', 'custom_label_3', 'custom_label_4']
				
		wr_fb.writerow(row_fb)
		#wr_fb_ad.writerow(row_fb)
		
		#row_google =['id', 'title', 'description', 'link', 'condition',
		#	'price', 'availability', 'image_link', 'mpn', 'brand', 
		#	'google product category', 'product type', 'custom_label_0', 'custom_label_1',
		#	'custom_label_2', 'custom_label_3', 'custom_label_4']
			
		row_google = [ 'id', 'title', 'description', 'link', 'image_link', 'additional_image_link', 'availability',
			'availability_date', 'expiration_date', 'price', 'google_product_category',
			'product_type', 'brand', 'gtin', 'MPN', 'material', 'size', 'item_group_id',
			'product_length', 'product_width', 'product_height', 'product_weight', 
			'product_detail', 'product_highlight', 'custom_label_0', 'custom_label_1',
			'custom_label_2', 'custom_label_3', 'custom_label_4', 'promotion_id',
			'shipping', 'ships_from_country', 'max_handling_time']	
		wr_google.writerow(row_google)
		#wr_google_ad.writerow(row_google)

		#non_gallery = csv.reader(ngal_file, delimiter=',')		

		curated = Curated_collection.objects.all()
		gallery = Gallery.objects.filter(is_published=True)

		##products = Stock_image.objects.filter(is_published = True)
		print("processing...." + str(curated.count()))
		cnt = 0

		processed_prods = []

		for c in curated:
			cnt = cnt + 1
			print(str(cnt) + "....")
			
			p = c.product

			if p.product_id in processed_prods:
				continue
			
			processed_prods.append(p.product_id)
			
			if p.is_published == False:
				print("skipping " + str(p.product_id) + ", it is not published.")
				continue

			## Skip the products that apprear to be victims of click fraud
			if p.product_id in [269770, 269777, 62834, 487444, 163008, 251877, 130528, 276423, 105996]:
				continue
			
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
			mount_size = 1 if image_width <= 26 else 2 
			moulding_id = 18 if image_width <= 26 else 24 
			
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

			## Get product category
			cat = Stock_image_stock_image_category.objects.filter(
				stock_image = p).first()

			#######################################
			# Check if this prod has a creative        ###
			# If it has skip, it will added at the end ###
			#######################################
			img_link = 'https://artevenue.com/static/' + p.url

			## Get product category
			#g_prod_type = "Home > Decor > Artworks > Framed Wall Art > Paintings > Set of Paingints > Gallery Walls"
			g_prod_type = "Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork"	
			cate = Stock_image_stock_image_category.objects.filter(
			stock_image_id = p.product_id).first()				
			cat = cate.stock_image_category.name.title()
			if cat.lower() == "miscellaneous" or cat.lower() ==  "miscellanuous":
				cat = 'Other'
			else:
				g_prod_type = g_prod_type + " > " + cat + " Paintings"

			############Product size & weight
			prod_height = image_height
			prod_width = image_width
			if moulding_id:
				moulding = Moulding.objects.filter(moulding_id = moulding_id).first()
				if moulding.width_inner_inches:
					prod_width = round(prod_width + (moulding.width_inner_inches*2))
					prod_height = round(prod_height + (moulding.width_inner_inches*2))
				if mount_size:
					prod_width = round(prod_width + (mount_size * 2))
					prod_height = round(prod_height + (mount_size * 2))

			############Product & Package Size : VARIANT ROW
			t_size = prod_width * prod_height
			if t_size <= 256:
				ship_weight = 1.25
			elif t_size <= 576:
				ship_weight = 1.5
			elif t_size <= 900:
				ship_weight = 2
			elif t_size <= 1600:
				ship_weight = 2.75
			else:
				ship_weight = 3.5
			
			#for f in fb_prod_for_ad:
			#	if str(p.product_id) == f:
			#		custom_label2 = 'AD'
			#		print('AD Prod: ' + f )
			desc = str(image_width + 4) + " X " + str(image_height + 4) + " inch framed wall art printed on paper, 1 inch black frame, 1 inch offwhite mount. Fully Customizable. "
			if p.image_type == '1':
				title = 'Framed Wall Art Titled "' + p.name + '", by ' + p.artist + '| Licensed Art Print '
			else:
				title = 'Framed Wall Art Painting Titled "' + p.name + '", by ' + p.artist + '| Licensed Art Print '

			
			custom_label1 = ''
			custom_label2 = ''
			custom_label4 = ''
			if str(p.product_id) not in fb_prods:
				custom_label1 = 'NEW'	

			if str(p.product_id) in ad_prods_singles:
				img_link = ad_prods_singles[str(p.product_id)]
				custom_label4 = 'SALE-AD'
			
			row_fb = [p.product_id, title[:140], desc, 'in stock', 'new', 
			str(item_price) + " INR", 'https://artevenue.com/art-print/' + str(p.product_id) + '/', img_link, 
			"Arte'Venue", '999', '1000', str(item_price) + " INR",  
			'', '', '', '',
			str(image_width + 4) + " X " + str(image_height + 4) + " inch" , '', 'Paper', '', 'IN::Ground:0.0 INR', str(ship_weight) + " kg", 
			'SINGLE', custom_label1, custom_label2, cat, custom_label4]
						
			wr_fb.writerow(row_fb)

			if str(p.product_id) not in google_prods:
				custom_label1 = 'NEW'
			
			row_google = [p.product_id, title[:140], desc, 
			'https://artevenue.com/art-print/' + str(p.product_id) + '/', img_link, '', 'in_stock',
			'2021-01-01', '', str(item_price) + ' INR', '500044', 
			g_prod_type, "ARTE'VENUE", '', p.part_number, 'Paper', str(image_width + 4) + " X " + str(image_height + 4) + " in" , '',
			'', str(image_width + 4) + " in", str(image_height + 4) + " in" , str(ship_weight) + " kg", 
			'', product_highlight, 'SINGLE', custom_label1, 
			custom_label2, cat, custom_label4, '',
			'IN:::0.0 INR', 'IN', '3'
			]			
			wr_google.writerow(row_google)


		##################################################################################
		##################################################################################
		##################################################################################
		####### GALLERY WALLS ###########
		##################################################################################
		##################################################################################
		for g in gallery:
			cnt = cnt + 1
			print(str(cnt) + "....")

			### GET GALLER WALL PRICE
			gallery_variation = Gallery_variation.objects.filter(gallery_id = g.gallery_id, is_parent = True).first()
			gallery_items = Gallery_item.objects.filter(gallery_id = g.gallery_id, 
				gallery_variation = gallery_variation)

			#gallery_items = gallery_items.values(
			#		'item_id', 'gallery_id', 'gallery_variation_id', 'product_id', 'product_name', 'product_type_id',
			#		'moulding_id', 'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id',
			#		'mount__name', 'mount__color', 'mount_size', 'board_id', 'acrylic_id', 'stretch_id', 'image_width', 
			#		'image_height', 'moulding__width_inner_inches')

			#g_prod_type = "Home > Decor > Artworks > Framed Wall Art > Paintings > Set of Paingints > Gallery Walls"
			g_prod_type = "Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork > Paintings > Set of Paingints > Gallery Walls"
			
			g_title = 'Gallery Wall Set: ' + g.title + ' A set of ' + str(g.set_of) + ", Customization Available"
			g_desc = 'Designer curated allery wall set. Contains ' + str(g.set_of) + ' framed art prints of licesed artworks. Covers wall area of approx ' + str(gallery_variation.wall_area_width) + " X " + str(gallery_variation.wall_area_height) + " inch (with 2 inch more gap between artworks)."

			gallery_variation_price = 0	
			gi_cnt = 0
			ship_weight = 0
			for gal_item in gallery_items:
				gi_cnt = gi_cnt + 1
				item_price = get_variation_item_price(gal_item.item_id)
				gallery_variation_price = gallery_variation_price + item_price
				i_desc = "\n\nArtwork " + str(gi_cnt) + ": " + "Printed on " + gal_item.print_medium_id.title() 				

				prod_height = gal_item.image_height
				prod_width = gal_item.image_width
				if gal_item.moulding:
					i_desc = i_desc + "\nFrame: " + gal_item.moulding.name + "( " + str(gal_item.moulding.width_inner_inches*2) + " inch)"
					if gal_item.moulding.width_inner_inches:
						prod_width = round(prod_width + (gal_item.moulding.width_inner_inches*2))
						prod_height = round(prod_height + (gal_item.moulding.width_inner_inches*2))
					if gal_item.mount and gal_item.print_medium_id == 'PAPER':					
						if mount_size:
							i_desc = i_desc + "\nMount: " + gal_item.mount.name + ", " + str(gal_item.mount_size) + " inch"
							prod_width = round(prod_width + (mount_size * 2))
							prod_height = round(prod_height + (mount_size * 2))
				else :
					if gal_item.print_medium_id == 'CANVAS' and gal_item.stretch_id == 1:
						i_desc = i_desc + "\nCanvas is stretched over wodden frame at the back"
				i_desc = i_desc + "\nFinished artwork size: " + str(prod_width) + " X " + str(prod_width)
				
				g_desc = g_desc + i_desc

				t_size = prod_width * prod_height
				if t_size <= 256:
					ship_weight = ship_weight + 1.25 
				elif t_size <= 576:
					ship_weight = ship_weight +  1.5
				elif t_size <= 900:
					ship_weight =  ship_weight + 2
				elif t_size <= 1600:
					ship_weight =  ship_weight + 2.75
				else:
					ship_weight =  ship_weight + 3.5
						
			
			custom_label1 = ''
			if 'G' + str(g.gallery_id) not in fb_prods:	## Same for FB and Google
				custom_label1 = 'NEW'

			custom_label2 = 'AD'				
			custom_label4 = ''
			if str(g.gallery_id) in ad_prods_gw:
				img_link = ad_prods_gw[str(g.gallery_id)]
				custom_label4 = 'SALE-AD'
			else: 	
				img_link = 'https://artevenue.com/static/' + g.room_view_url

			row_fb = ['G' + str(g.gallery_id), g_title, g_desc, 'in stock', 'new', 
				str(gallery_variation_price) + ' INR', 'https://artevenue.com/gallery-wall/' + str(g.gallery_id) + '/', 			 
				img_link, "ARTE'VENUE", '999', '1000', str(gallery_variation_price) + " INR",  
				'', '', '', '',
				str(gallery_variation.wall_area_width) + " X " + str(gallery_variation.wall_area_height) + " inch", 
				'', '', '', 'IN::Ground:0.0 INR', str(ship_weight) + " kg", 
				'GALLERY_WALL', custom_label1, custom_label2, str(g.room.name), custom_label4
			]
						
			wr_fb.writerow(row_fb)


			row_google = ['G' + str(g.gallery_id), 'Gallery Wall: ' + g.title + ', Set of ' + str(g.set_of)  + ', Customization Available', 
				g_desc, 'https://artevenue.com/gallery-wall/' + str(g.gallery_id) + '/', img_link,
				'', 'in_stock',
				'2021-01-01', '', str(gallery_variation_price) + ' INR', '500044',
				g_prod_type,  "ARTE'VENUE", '', p.part_number, '', str(gallery_variation.wall_area_width) + " X " + str(gallery_variation.wall_area_height) + " inch (appox wall area coverd)" , '',
				'', str(gallery_variation.wall_area_width) + " in", str(gallery_variation.wall_area_height) + " in", str(ship_weight) + " kg",
				'', product_highlight, 'GALLERY_WALL', custom_label1, 
				custom_label2, str(g.room.name), custom_label4, '',
				'IN:::0.0 INR', 'IN', '3'
			]
			wr_google.writerow(row_google)

			
		'''
		##################################################################################
		##################################################################################
		##################################################################################
		## Include all products that have creatives ##
		## but not already included in the feed     ##
		##################################################################################
		##################################################################################
		##################################################################################
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
					if prod.artist == 'Huynh, Duy':
						if prod.aspect_ratio > 1:
							image_height = 16
							image_width = round(h * aspect_ratio)
						else:
							image_width = 16
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

					custom_label2 = 'AD'

					row_fb = [prod.product_id, title[:140], desc, 'in stock', 'new', item_price, 
					'https://artevenue.com/art-print/' + str(prod.product_id) + '/', 
					n[1], 
					"Arte'Venue", '', '', '', '', '', 
					'Home & Garden > Decor > Artwork', '', '', 
					cat.stock_image_category.name.title(), '', '', 'Free Shipping', '', 
					str(image_width + 4) + " X " + str(image_height + 4) + " inch" + 
					'', '', custom_label2, '', '']

					wr_fb.writerow(row_fb)
					wr_fb_ad.writerow(row_fb)

					row_google = [prod.product_id, title[:140], desc, 
					'https://artevenue.com/art-print/' + str(prod.product_id) + '/',
					'new', str(item_price) + ' INR', 'in stock', 
					n[1], 
					prod.part_number, "Arte'Venue", '500044', 
					cat.stock_image_category.name.title(), '', '', custom_label2, '', ''
					#'paintings > paintings online > wall art > paintings for home > paintings for living room > paintings for bedroom'
					]

					wr_google.writerow(row_google)
					wr_google_ad.writerow(row_google)
					
		'''
		##################################################################################
		##################################################################################
		##################################################################################
		## Sets and Best sellers 					 
		##################################################################################
		##################################################################################
		##################################################################################
		sets = Stock_collage.objects.filter(is_published = True)
		if not sets:	
			return
			
		for set in sets:
			try:
				has_specs = (set.stock_collage_specs is not None)
			except Stock_collage_specs.DoesNotExist:
				print("No spces. Skipped..." + str(set.product_id) )
				continue
			print("Printing Set: " + str(set.product_id))
			
			image_width = 10
			if set.stock_collage_specs:
				iwidth = str(set.stock_collage_specs.image_width)
				if iwidth and iwidth != 'None' :
					image_width = int(iwidth)
				else:
					image_width = 10
			image_height = round( image_width / set.aspect_ratio )

			if set.stock_collage_specs.print_medium_id == 'PAPER':
				if set.aspect_ratio > 1:
					mount_size = 1 if image_width <= 18 else 2 if image_width <= 26 else 3 if image_width <= 34 else 4
				else:
					mount_size = 1 if image_height <= 18 else 2 if image_height <= 26 else 3 if image_height <= 34 else 4
			else :
				mount_size = 0
				
			prod_data = {}			
			############Common
			prod_data['hsn_code'] = '97020000'
			prod_data['brand'] = "ARTE'VENUE"
			prod_data['country_of_origin'] = "India"
			prod_data['prod_type'] = "Wall Art"
			prod_data['frame_type'] = 'Hanging'
			prod_data['frame_material'] = 'Polystyrene'
			prod_data['handling_time'] = 3
			prod_data['seller_address'] = 'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com'
			
			############SKU
			prod_data['best_sellers_sku_prefix'] = 'S-'
			prod_data['sets_sku_prefix'] = 'ST-'
			prod_data['gw_sku_prefix'] = 'GW-'
			prod_data['prod_sku'] = ''

			
			############Product
			prod_data['part_number'] = prod_data['sets_sku_prefix'] + str(set.product_id)
			prod_data['prod_name'] = prod_data['prod_desc'] = prod_data['prod_title'] = ''
			prod_data['prod_mrp'] = prod_data['prod_price'] = prod_data['prod_tax'] = 0 
			prod_data['quantity'] = 1000	
			prod_data['num_pieces'] = 0
			prod_data['print_surface'] = set.stock_collage_specs.print_medium_id.title()
			
			############Product features, Images, Videos
			prod_data['features_1'] = "The best quality giclee prints produced at a very high resolution with full saturation and are fade resistant. Large format inkjet printers with archival inks are used to ensure consistent quality. Each artwork has an associated copyright and is licensed from the artist."
			if set.stock_collage_specs.print_medium_id == 'PAPER':
				prod_data['features_2'] = "Coated premium matte paper 230 GSM. Bright white, smooth finish matte, top-coated with an ink-receptive layer."
			else:
				prod_data['features_2'] = "Artistic matte cotton canvas 410 GSM which is matte finished, crack-resistant, water-resistant, and top-coated with an ink-receptive layer."
				
			prod_data['features_3'] = "Frame is made of high density polystyrene which is moisture resistant, premium finish, durable and light weight."
			prod_data['features_4'] = "All artworks are ready to hang and come with necessary hooks."
			
			prod_data['display_image'] = set.stock_collage_specs.display_url
			prod_data['prod_url'] = "https://artevenue.com/wall-art-collage-set/" + str(set.product_id) + "/"
			prod_data['video_1'] = 'https://youtu.be/6vRss_YY48I'
			prod_data['video_2'] = 'https://youtu.be/vSrersiMjWk'

			############Product Attributes
			prod_data['shape'] = ''	
			prod_data['prod_tax_percentage'] = '12%'
			prod_data['prod_condition'] = 'New'
			
			############Product & Package Size 
			prod_data['prod_width'] = prod_data['prod_height'] = prod_data['prod_length'] = prod_data['prod_weight'] = 0
			prod_data['package_width'] = prod_data['package_height'] = prod_data['package_length'] = prod_data['package_weight'] = 0

			############Offer
			prod_data['list_price'] = prod_data['sale_price'] = 0
			prod_data['available_from_date'] = '2021-06-01'
			prod_data['sale_start_date'] = '2021-06-01'
			prod_data['sale_end_date'] = '2023-06-01'
					
			if set.set_of > 1:
				sku_prefix = prod_data['sets_sku_prefix']
			else:
				sku_prefix = prod_data['best_sellers_sku_prefix']
			
			if set.set_of > 1:
				prod_name = "Framed Wall Art Set of " + str(set.set_of) + " on " + set.stock_collage_specs.print_medium_id.title() + ", Title: " + set.name + ", Customization Available"
			else:	
				prod_name = "Framed Wall Art on " + set.stock_collage_specs.print_medium_id.title()  + ", Title: " + set.name + ", Customization Available"
			
			if set.set_of > 1:
				prod_desc = "A framed wall art set of " + str(set.set_of) + " artworks."
			else:
				prod_desc = "Framed wall art."
			
			if set.set_of > 1:
				search_terms = "framed wall art set, set of " + str(set.set_of) + " paintings"
			else:
				search_terms = "framed wall art, framed paitings"

			
			items = Collage_stock_image.objects.filter(stock_collage_id = set.product_id)		

			pck_max_width = 0
			pck_max_height = 0
			_wall_area_width = 0
			prod_total = 0
			prod_sub_total = 0
			prod_tax = 0
			prod_mrp = 0			
			p_cnt = 0
			for p in items:	
				p_cnt = p_cnt + 1
				product_type_id = "STOCK-IMAGE"
				####################################################
				#  Get the item price
				####################################################
				price = get_prod_price(p.stock_image_id, 
						prod_type = product_type_id,
						image_width=image_width, 
						image_height=image_height,
						print_medium_id = set.stock_collage_specs.print_medium_id,
						acrylic_id = set.stock_collage_specs.acrylic_id,
						moulding_id = set.stock_collage_specs.moulding_id,
						mount_size = set.stock_collage_specs.mount_size,
						mount_id = set.stock_collage_specs.mount_id,
						board_id = set.stock_collage_specs.board_id,
						stretch_id = set.stock_collage_specs.stretch_id)
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
				item_total_mrp = item_total
			
				prod_total = prod_total + item_total
				prod_sub_total = prod_sub_total + item_sub_total
				prod_tax = prod_tax + item_tax
				prod_mrp = prod_mrp + item_total_mrp			

				#####################################################
				## Also gather data for individual products
				#####################################################
				pck_size_width = image_width
				pck_size_height = image_height

				prod_height = image_height
				prod_width = image_width
				if set.stock_collage_specs.moulding:
					if set.stock_collage_specs.moulding.width_inner_inches:
						prod_width = round(prod_width + (set.stock_collage_specs.moulding.width_inner_inches*2))
						prod_height = round(prod_height + (set.stock_collage_specs.moulding.width_inner_inches*2))
						pck_size_width = pck_size_width + (set.stock_collage_specs.moulding.width_inner_inches*2)
						pck_size_height = pck_size_height + (set.stock_collage_specs.moulding.width_inner_inches*2)
					if set.stock_collage_specs.mount and set.stock_collage_specs.print_medium_id == 'PAPER':
						if mount_size:
							prod_width = round(prod_width + (mount_size * 2))
							prod_height = round(prod_height + (mount_size * 2))
							pck_size_width = pck_size_width + (mount_size * 2)
							pck_size_height = pck_size_height + (mount_size * 2)

				if _wall_area_width == 0:
					_wall_area_width = prod_width
				else:
					_wall_area_width = _wall_area_width + prod_width + 2
				
				pck_size_width = pck_size_width + 2
				pck_size_height = pck_size_height + 2

				if pck_size_width > pck_max_width:
					pck_max_width = pck_size_width
				if pck_size_height > pck_max_height:
					pck_max_height = pck_size_height
				pck_size_length = 2 * set.set_of

				############Product & Package Size : VARIANT ROW
				t_size = prod_width * prod_height
				if t_size <= 256:
					ship_weight = 1.25 * set.set_of
				elif t_size <= 576:
					ship_weight = 1.5 * set.set_of
				elif t_size <= 900:
					ship_weight = 2 * set.set_of
				elif t_size <= 1600:
					ship_weight = 2.75 * set.set_of
				else:
					ship_weight = 3.5 * set.set_of

				if set.set_of > 1:
					prod_desc = prod_desc + "\n\nArtwork " + str(p_cnt) + ": Finished Size " + str(prod_width) + " X " + str(prod_height) + " inches."
				else:
					prod_desc = prod_desc + "\nFinished Size: " + str(prod_width) + " X " + str(prod_height) + " inches."
					
				prod_desc = prod_desc + "\nPrint Surface: " + set.stock_collage_specs.print_medium_id.title() + ". "
				prod_desc = prod_desc + "\nPrint Size: " + str(image_width) + " X " + str(image_height) + " inches."
				if set.stock_collage_specs.moulding:
					prod_desc = prod_desc + "\nFrame: " + set.stock_collage_specs.moulding.name + " (" + str(set.stock_collage_specs.moulding.width_inches) + " inch)." if set.stock_collage_specs.moulding_id else '' 
				if set.stock_collage_specs.mount_id and set.stock_collage_specs.print_medium_id == 'PAPER' and set.stock_collage_specs.moulding:
					prod_desc = prod_desc + "\nMount: " + str(mount_size) + " inch, " + set.stock_collage_specs.mount.name.title() + "." if set.stock_collage_specs.mount_id else ''
				
				if not set.stock_collage_specs.moulding_id and set.stock_collage_specs.print_medium_id == 'CANVAS':
					prod_desc = prod_desc + "\nCanvas is stretched over a wooden frame at the back. Frame not visible from the front and sides."				

				search_terms = search_terms + p.stock_image.key_words
				
			if set.set_of > 1:
				#g_prod_type = "Home > Decor > Artworks > Framed Wall Art > Paintings > Set of Paintings"
				g_prod_type = "Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork > Paintings > Set of Paintings"	

			else:
				#g_prod_type = "Home > Decor > Artworks > Framed Wall Art > Paintings"
				g_prod_type = "Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork"	

			
			cate = ''
			if set.stock_image_category:
				g_prod_type	= g_prod_type + " > " + set.stock_image_category.name
				cate = set.stock_image_category.name
			
			prod_data['prod_sku'] = prod_data['sets_sku_prefix'] + str(set.product_id)

			custom_label_1 = ''

			if prod_data['prod_sku'] not in fb_prods:	## Same for FB & Google
				custom_label_1 = 'NEW'
				
			custom_label_2 = 'AD'
			custom_label4 = ''
			if str(set.product_id) in ad_prods_sets:
				img_link = ad_prods_sets[str(set.product_id)]
				custom_label4 = 'SALE-AD'
			else:
				img_link = 'https://artevenue.com/static/' + set.stock_collage_specs.display_url
			row_fb = [prod_data['prod_sku'], prod_name, prod_desc, 'in stock', 'new', 
				str(prod_mrp) + ' INR', 'https://artevenue.com/wall-art-collage-set/' + str(set.product_id) + '/', 			 
				img_link, "ARTE'VENUE", '999', '1000', str(prod_mrp) + ' INR',  
				'', '', '', '',
				str(prod_width) + " X " + str(prod_height) + " in" + " (Each)" if set.set_of > 1 else str(prod_width) + " X " + str(prod_height) + " in", 
				'', prod_data['print_surface'], '', 'IN::Ground:0.0 INR', str(ship_weight) + " kg", 
						'SET', custom_label1, custom_label2, cate, custom_label4
			]
			wr_fb.writerow(row_fb)

			row_google = [ prod_data['prod_sku'], prod_name, prod_desc,
				'https://artevenue.com/wall-art-collage-set/' + str(set.product_id) + '/',
				img_link,  '', 'in_stock', '2021-01-01', '', str(prod_mrp) + ' INR', '500044', 
				g_prod_type, "ARTE'VENUE", '', prod_data['part_number'], prod_data['print_surface'], 
				str(prod_width) + " X " + str(prod_height) + " in" + " (Each)" if set.set_of > 1 else str(prod_width) + " X " + str(prod_height) + " in",
				'',
				'', str(prod_width) + " in", str(prod_height) + " in", str(ship_weight) + " kg",
				'', product_highlight,
				'SET', custom_label_1, custom_label_2, cate, custom_label4, '', 
				'IN:::0.0 INR', 'IN', '3'
			]		
			wr_google.writerow(row_google)
			


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


def generate_livspacestore_feed():

	if env == 'PROD':
		av_single_img_file = '/home/artevenue/website/estore/static/feeds/livspacestore/single_img_prod_input.csv'
		av_set_file = '/home/artevenue/website/estore/static/feeds/livspacestore/set_input.csv'
		av_gw_file = '/home/artevenue/website/estore/static/feeds/livspacestore/gw_input.csv'
		av_feed = '/home/artevenue/website/estore/static/feeds/livspacestore/av_feed.csv'
		img_loc = '/home/artevenue/website/estore/static/feeds/livspacestore/images/'
		img_url = 'https://artevenue.com/static/feeds/livspacestore/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		av_single_img_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/single_img_prod_input.csv'
		av_set_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/set_input.csv'
		av_gw_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore//gw_input.csv'
		av_feed = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/av_feed.csv'
		img_loc = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/images/'
		img_url = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/images/'
		av_url = 'https://artevenue.com/static/'
	
	with open(av_feed, 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row =["product_type", "artevenue_sku", 'brand', 'product_id', 'product_type',
			'product_description', 'product_title', 'country_of_origin', 'HSN_Code',
			'Maximum Retail Price(incl GST)', 'Main Image URL', 
			'Quantity', 			
			'Other Image URL1', 'Other Image URL2', 'Other Image URL3', 'Other Image URL4', 'Other Image URL5', 
			## Variation

			## Basic Info
			'update_delete', 'manufacturer',

			## Discovery
			'bullet_point1', 'bullet_point2', 'bullet_point3',
			'bullet_point4', 'bullet_poin5', 'frame_type', 'theme', 'size', 'search_terms',
			
			## Dimensions
			'Item Width Unit of Measure', 'Item Height Unit of Measure', 'Item Width', 
			'Item Height', 'Shape', 'Item Length Unit of Measure', 
			'Item Length', 'Unit Count Type', 'Unit Count',
			
			## Fulfilment
			'Package Height Unit of Measure', 'Package Length', 'Package Width',
			'Package Weight Unit of Measure', 'Package Height', 'Package Width Unit of Measure',
			'Package Length Unit of Measure', 'Package Weight',
			
			## Offer
			'Offer Start Date', 'Offer End Date', 'Currency', 'Max Order Quantity',
			'GST %', 'Shipping Time', 'Delivery Time',
			'Condition', 'Sale Price(incl GST)', 
			'Sale Start Date', 'Sale End Date'
		]

		wr.writerow(row)

		#####################################
		### Get products #######
		#####################################
		singles = Collage_stock_image.objects.filter(stock_collage__set_of = 1, stock_image__is_published = True)
		#sets = Collage_stock_image.object.filter(stock_image__set_of__gt = 1, is_published = True)
		#gw = Gallery_item.object.filter(is_published = True)
		
		for h in singles:
			print("processing..." + str(h.stock_collage.product_id) )
			
			if h.stock_image.aspect_ratio <= 1:
				## Vertical & Square
				widths = [10, 14, 18, 24, 30]
			elif h.stock_image.aspect_ratio == 1:
				## Sqaure
				widths = [10, 14, 18, 24, 30]
			else:
				## Horizontal
				widths = [14, 18, 24, 30, 36]
			
				
			sku_suf = 0
			for wd in widths:
				sku_suf = sku_suf + 1
				image_width = wd
				image_height = round( wd / h.stock_image.aspect_ratio )
				
				length = formatNumber(image_height) 
				if h.stock_collage.stock_collage_specs.moulding:
					if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
						length = formatNumber(length + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2))
					if h.stock_collage.stock_collage_specs.mount:
						if h.stock_collage.stock_collage_specs.mount_size:
							length = formatNumber(length + (h.stock_collage.stock_collage_specs.mount_size * 2))
				
				breadth = formatNumber(image_width)
				if h.stock_collage.stock_collage_specs.moulding:
					if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
						breadth = formatNumber(breadth + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2))
					if h.stock_collage.stock_collage_specs.mount:
						if h.stock_collage.stock_collage_specs.mount_size:
							breadth = formatNumber(breadth + (h.stock_collage.stock_collage_specs.mount_size * 2))

				
				catObj = Stock_image_stock_image_category.objects.filter(stock_image_id = h.stock_image_id).first()
				cat = catObj.stock_image_category.name.title()

				prod_details = cat + " Artwork with frame," + " Title: " + h.stock_image.name + ", Artist: " + h.stock_image.artist + ".\nPrinted on: " + h.stock_collage.stock_collage_specs.print_medium_id.title() + "; Licensed Art Print. "
				prod_details = prod_details + "Print Size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + "; \n"
				incl_components = "One piece " + cat + " art with frame, printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + "; "
				incl_components = incl_components + "Print Size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + "; "
				if h.stock_collage.stock_collage_specs.print_medium_id == 'PAPER':
					if h.stock_collage.stock_collage_specs.moulding_id:
						bullet1 = 'Frames Wall Art. Licensed Art print on ' + h.stock_collage.stock_collage_specs.print_medium_id.title() + ', size: ' + str(formatNumber(image_width + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2) + (h.stock_collage.stock_collage_specs.mount_size *2) )) + " X " + str(formatNumber(image_height + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2) + ( h.stock_collage.stock_collage_specs.mount_size * 2) )) + " inch."
					else:
						bullet1 = "Printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + ", size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch."
					prod_details = prod_details + "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
				else:
					if h.stock_collage.stock_collage_specs.moulding_id:
						bullet1 = 'Printed on ' + h.stock_collage.stock_collage_specs.print_medium_id.title() + ', size: ' + str(formatNumber(image_width + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2) )) + " X " + str(formatNumber(image_height + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2) )) + " inch."
					else:
						bullet1 = "Printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + ", size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch."
					prod_details = prod_details + "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \n"
				bullet2 = ''
				t_size = ''
				if h.stock_collage.stock_collage_specs.moulding_id:
					prod_details = prod_details + "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch). Frame is made of polystyrene, which is light weight, long lasting, premium finish.\n"
					incl_components = incl_components + "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch, Polystyrene). "
					bullet2 = "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch). It's a high quality frame made of Polystyrene, which is light weight, long lasting, premium finish." 
				if h.stock_collage.stock_collage_specs.mount_id:
					prod_details = prod_details + "Mount: " + str(formatNumber(h.stock_collage.stock_collage_specs.mount_size)) + " inch, Color: " + h.stock_collage.stock_collage_specs.mount.name.lower() + ", it enhances the look of this artwork. \n"
					incl_components =  incl_components + "Mount: " + str(formatNumber(h.stock_collage.stock_collage_specs.mount_size)) + " inch, Color: " + h.stock_collage.stock_collage_specs.mount.name.lower() + ". "
					bullet2 = bullet2 + ", " +str(formatNumber(h.stock_collage.stock_collage_specs.mount_size)) + " inch " + h.stock_collage.stock_collage_specs.mount.name.lower() + " mount adds classy look to this art. "
				## Total Size
				t_size_width = image_width
				t_size_height = image_height
				if h.stock_collage.stock_collage_specs.moulding:
					if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
						t_size_width = t_size_width + h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2
						t_size_height = t_size_height + h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2
				if h.stock_collage.stock_collage_specs.mount:
					t_size_width = t_size_width + h.stock_collage.stock_collage_specs.mount_size*2
					t_size_height = t_size_height + h.stock_collage.stock_collage_specs.mount_size*2
				
				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details + "Product Size (with frame): " + t_size
				incl_components = incl_components + "Product Size  (with frame): " + t_size
				
				bullet3 = ''
				if h.stock_collage.stock_collage_specs.print_medium_id == "PAPER":
					if h.stock_collage.stock_collage_specs.acrylic_id:
						prod_details = prod_details + "\nThe artwork is covered with clear acrylic for added protection, durability and clear visibility. Acrylic is light weight and durable."
						incl_components = incl_components + "Acrylic covered; "
					bullet3 = "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility."
				else:
					bullet3 = "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions."
					
				if h.stock_collage.stock_collage_specs.stretch_id and h.stock_collage.stock_collage_specs.print_medium_id == 'CANVAS' and (h.stock_collage.stock_collage_specs.moulding_id == None or h.stock_collage.stock_collage_specs.moulding_id == 0):
					prod_details = prod_details + "Canvas Stretched; "

				search_terms = ( cat + " paintings, wall paintings, wall art, paintings for home decor, art print, paintings with frame, paintings for living room, paintings for bed room, wall decor " + h.stock_image.key_words.replace('|', ', '))[:150]
				
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Print on ' + h.stock_collage.stock_collage_specs.print_medium_id.title()
				qty = '100'
				
				product_type_id =  'STOCK-IMAGE'

				#  Get the item price
				price = get_prod_price(h.stock_image_id, 
						prod_type= product_type_id,
						image_width=image_width, 
						image_height=image_height,
						print_medium_id = h.stock_collage.stock_collage_specs.print_medium_id,
						acrylic_id = h.stock_collage.stock_collage_specs.acrylic_id,
						moulding_id = h.stock_collage.stock_collage_specs.moulding_id,
						mount_size = h.stock_collage.stock_collage_specs.mount_size,
						mount_id = h.stock_collage.stock_collage_specs.mount_id,
						board_id = h.stock_collage.stock_collage_specs.board_id,
						stretch_id = h.stock_collage.stock_collage_specs.stretch_id)
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

				
				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"
				
				item_total_mrp = item_total
				
				prod_name = "Title: " + h.stock_image.name + "| Framed Wall Art on "  + h.stock_collage.stock_collage_specs.print_medium_id.title() + " | " + t_size

				update_delete = "Update"
				if image_width > h.stock_image.max_width or image_height > h.stock_image.max_height:
					update_delete = "Delete"
				
				finish_type = 'Matt finish'
				style_name = cat
				power_source_type = ''
				packer_contact_information = ''
				packer_contact_name = ''
				target_audience_base = ''
				length_range = ''
				importer_contact_information = ''
				frame_type = 'Polystyrene'
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


				av_sku = ("S-" + str(h.collage_id) + "-" + str(sku_suf))

				################################
				### 3D IMAGE 
				################################
				stretched_canvas = 'NO'
				if h.stock_collage.stock_collage_specs.print_medium_id == 'CANVAS' and (h.stock_collage.stock_collage_specs.moulding_id == None or h.stock_collage.stock_collage_specs.moulding_id == 0) and h.stock_collage.stock_collage_specs.stretch_id == 1:
					stretched_canvas = 'YES'

				from django.http import HttpRequest
				request = HttpRequest()
				framed_img_3d = get_FramedImage_by_id(request, h.stock_image_id, h.stock_collage.stock_collage_specs.moulding_id, 
					mount_color = h.stock_collage.stock_collage_specs.mount.color if h.stock_collage.stock_collage_specs.mount else '' , 
					mount_size=float(h.stock_collage.stock_collage_specs.mount_size) if h.stock_collage.stock_collage_specs.mount_size else 0, 
					user_width=float(image_width), prod_type=product_type_id, 
					stretched_canvas=stretched_canvas, imgtilt='YES', dropshadow='NO' )
				
				aspect_ratio = framed_img_3d.width / framed_img_3d.height
				framed_img_3d = framed_img_3d.resize( (1200, int(round(1200/aspect_ratio))) )				
				
				img_3d_name =  av_sku + "_3d.jpg" 
				
				# save image
				ifile_3d = Path(img_loc + img_3d_name)
				if ifile_3d.is_file():
					print("Image already available...skipping - Main image")
				else:
					framed_img_3d.save(img_loc + img_3d_name)
				
				img_3d_url = img_url + img_3d_name

				################################
				### 2D IMAGE 
				################################
				stretched_canvas = 'NO'
				if h.stock_collage.stock_collage_specs.print_medium_id == 'CANVAS' and (h.stock_collage.stock_collage_specs.moulding_id == None or h.stock_collage.stock_collage_specs.moulding_id == 0) and h.stock_collage.stock_collage_specs.stretch_id == 1:
					stretched_canvas = 'YES'

				from django.http import HttpRequest
				request = HttpRequest()
				framed_img_3d = get_FramedImage_by_id(request, h.stock_image_id, h.stock_collage.stock_collage_specs.moulding_id, 
					mount_color = h.stock_collage.stock_collage_specs.mount.color if h.stock_collage.stock_collage_specs.mount else '' , 
					mount_size=float(h.stock_collage.stock_collage_specs.mount_size) if h.stock_collage.stock_collage_specs.mount_size else 0, 
					user_width=float(image_width), prod_type=product_type_id, 
					stretched_canvas=stretched_canvas, imgtilt='NO', dropshadow='NO' )
				
				aspect_ratio = framed_img_3d.width / framed_img_3d.height
				framed_img_2d = framed_img_3d.resize( (1200, int(round(1200/aspect_ratio))) )				
				
				img_2d_name =  av_sku + "_2d.jpg" 
				
				# save image
				ifile_2d = Path(img_loc + img_2d_name)
				if ifile_2d.is_file():
					print("Image already available...skipping - Main image")
				else:
					framed_img_2d.save(img_loc + img_2d_name)
				
				img_2d_url = img_url + img_2d_name
					
				row =['wallart', av_sku, "ARTE'VENUE", 
					h.stock_image.product_id, 'Framed Artwork',
					prod_details, prod_name, 'India', '97020000', 
					item_total_mrp if item_total_mrp > 0 else 0.01, av_url + h.stock_collage.stock_collage_specs.display_url, 
					qty, 
					
					##Images
					img_3d_url, img_2d_url, '', '', '',

					## Variation
						
					## Basic Info
					update_delete, 'Montage Art Pvt Ltd', 
					
					## Discovery
					bullet1, bullet2, bullet3, 
					'Comes with hooks and is ready to be hung on the wall.', 
					'This is a licensed artwork. We produce premium quality art prints from licensed images, frame it and deliver. Your satisfaction is guaranteed.', 
					frame_type, theme, p_size, search_terms, 

					## - Diamensions
					'IN', 'IN', t_size_width, t_size_height, sq_re,
					'IN', 2, 'Count', 1,

					## Fulfilment
					'IN', 3, str(t_size_width + 3), 'KG', str(t_size_height + 3), 'IN', 'IN', ship_weight, 
					
					##-- Offer
					'03/23/2021', '12-31-2022',  'INR', 100, 
					'12%', '2-3 days', 
					'Delivered by courier to most cities in India in 4-7 days', 
					'New', item_total if item_total > 0 else 0.01, 
					'03/23/2021', '12/31/2022',
					]
					
				wr.writerow(row)




def generate_av_best_sellers_feed():

	if env == 'PROD':
		av_single_img_file = '/home/artevenue/website/estore/static/feeds/livspacestore/single_img_prod_input.csv'
		av_set_file = '/home/artevenue/website/estore/static/feeds/livspacestore/set_input.csv'
		av_gw_file = '/home/artevenue/website/estore/static/feeds/livspacestore/gw_input.csv'
		av_feed = '/home/artevenue/website/estore/static/feeds/AV/av_amz_feed.csv'
		av_amz_feed = '/home/artevenue/website/estore/static/feeds/AV/av_amz_feed.csv'
		av_livspace_feed = '/home/artevenue/website/estore/static/feeds/AV/av_livspacestore_feed.csv'
		av_tatacliq_feed = '/home/artevenue/website/estore/static/feeds/AV/av_tatacliq_feed.csv'
		img_loc = '/home/artevenue/website/estore/static/feeds/AV/images/'
		img_url = 'https://artevenue.com/static/feeds/AV/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		av_single_img_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/single_img_prod_input.csv'
		av_set_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/set_input.csv'
		av_gw_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore//gw_input.csv'
		av_feed = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/av_amz_feed.csv'
		av_amz_feed = 'C:/artevenue/PRODUCT_FEEDS/AV/av_amz_feed.csv'
		av_livspace_feed = 'C:/artevenue/PRODUCT_FEEDS/AV/av_livspacestore_feed.csv'
		av_tatacliq_feed = 'C:/artevenue/PRODUCT_FEEDS/AV/av_tatacliq_feed.csv'
		img_loc = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		img_url = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		av_url = 'https://artevenue.com/static/'
	
	with open(av_amz_feed, 'w', newline='') as amzfile, open(av_livspace_feed, 'w', newline='') as livfile, open(av_tatacliq_feed, 'w', newline='') as tatafile:
		wr_amz = csv.writer(amzfile, quoting=csv.QUOTE_ALL)
		wr_liv = csv.writer(livfile, quoting=csv.QUOTE_ALL)
		wr_tata = csv.writer(tatafile, quoting=csv.QUOTE_ALL)
		
		
		row_amz =['product_type', 'Seller SKU', 'Brand', 'Product ID', 'Product ID Type',
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

		wr_amz.writerow(row_amz)

		row_tata = [ 'product_type', 'hsn_code', 'sku_code', 'title, name', 'description', 'ean_code', 'length', 'width', 
					'weight', 'lead_time', 'warranty_type', 'warranty_period_months', 'brand_name', 'brand_description', 
					'mrp', 'collection_name', 'color_family', 'color', 'model_number', 'season', 'size', 'material', 'material_composition', 
					'secondary material', 'feature1', 'feature2', 'feature3', 'feature4', 'wash_care', 'care_instructions, pattern', 
					'battery_type', 'warranty_details', 'candle_type', 'fragrance_type', 'quantity', 'artpiece_type', 'set', 
					'set_component_name1', 'set_component1_quantity', 'set_component1_dimensions',
					'set_component_name2', 'set_component2_quantity', 'set_component2_dimensions',
					'set_component_name3', 'set_component3_quantity', 'set_component3_dimensions',
					'set_component_name4', 'set_component4_quantity', 'set_component4_dimensions',
					'set_component_name5', 'set_component5_quantity', 'set_component5_dimensions',
					'set_component_name6', 'set_component6_quantity', 'set_component6_dimensions',
					'country_of_origin', 'manufacturer', 'importer', 'packer', 
					'image_links', 'video_links'
					]
		wr_tata.writerow(row_tata)

		#################################################################
		#################################################################
		#####################################
		##  BEST SELLER  products #######
		#####################################
		#################################################################
		#################################################################
		singles = Collage_stock_image.objects.filter(stock_collage__set_of = 1, stock_image__is_published = True)
		#sets = Collage_stock_image.object.filter(stock_image__set_of__gt = 1, is_published = True)
		#gw = Gallery_item.object.filter(is_published = True)
		
		for h in singles:
			print("processing..." + str(h.stock_collage.product_id) )
			#################################################################
			###### Create parent record
			#################################################################
			image_width = 10
			image_height = round( image_width / h.stock_image.aspect_ratio )


			length = formatNumber(image_height) 
			if h.stock_collage.stock_collage_specs.moulding:
				if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
					length = formatNumber(length + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2))
				if h.stock_collage.stock_collage_specs.mount:
					if h.stock_collage.stock_collage_specs.mount_size:
						length = formatNumber(length + (h.stock_collage.stock_collage_specs.mount_size * 2))
			
			breadth = formatNumber(image_width)
			if h.stock_collage.stock_collage_specs.moulding:
				if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
					breadth = formatNumber(breadth + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2))
				if h.stock_collage.stock_collage_specs.mount:
					if h.stock_collage.stock_collage_specs.mount_size:
						breadth = formatNumber(breadth + (h.stock_collage.stock_collage_specs.mount_size * 2))

			parentage = 'Parent'
			variation = ''
			col = ''
			col_map = 'Multi'
			p_size = 'Size: ' + str(10) + '" X ' + str(10) + '" (inches)'
			size_map = ''
			qty = '1'
			item_total = 0
			item_total_mrp = 0
			parent_amz_sku = ("S-" + str(h.collage_id) + "-0")
			img_3d_url = ''
			img_2d_url = ''
			bullet1, bullet2, bullet3 = '', '', ''
			finish_type = 'Matt finish'
			update_delete = "Update"
			if image_width > h.stock_image.max_width or image_height > h.stock_image.max_height:
				update_delete = "Delete"
			
			catObj = Stock_image_stock_image_category.objects.filter(stock_image_id = h.stock_image_id).first()
			cat = catObj.stock_image_category.name.title()
			style_name = cat


			color_name = ''
			occassion = ''
			finish_type = 'Matt finish'
			pattern_name = ''
			style_name = 'A Set of Paintings'
			scent_name = ''
			
			power_source_type = ''
			packer_contact_information = ''
			packer_contact_name = ''
			target_audience_base = ''
			length_range = ''
			importer_contact_information = ''
			frame_type = 'Polystyrene'
			theme = cat
			department = ''
			item_volume = ''
			display_volume = ''	

			search_terms = ( cat + " paintings, wall paintings, wall art, paintings for home decor, art print, paintings with frame, paintings for living room, paintings for bed room, wall decor " + h.stock_image.key_words.replace('|', ', '))[:150]

			if cat == '' or cat == 'Miscellanuous':
				prod_details = "Artwork with frame - "
			else:
				prod_details = cat + " theme artwork with frame - "
			prod_details = prod_details  + " Title: " + h.stock_image.name + ", Artist: " + h.stock_image.artist + ".\nFramed wall art. Printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + ". Licensed art print. \n"
			prod_details =  prod_details + "Print size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch. \n"
			incl_components = "One piece " + cat + " art with frame, printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + "; "
			incl_components = incl_components + "Print Size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + "; "
			if h.stock_collage.stock_collage_specs.print_medium_id == 'PAPER':
				if h.stock_collage.stock_collage_specs.moulding_id:
					bullet1 = 'Printed on ' + h.stock_collage.stock_collage_specs.print_medium_id.title() + ', size: ' + str(formatNumber(image_width + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2) + (h.stock_collage.stock_collage_specs.mount_size *2) )) + " X " + str(formatNumber(image_height + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2) + ( h.stock_collage.stock_collage_specs.mount_size * 2) )) + " inch."
				else:
					bullet1 = "Printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + ", size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch."
				prod_details = prod_details + "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
			else:
				if h.stock_collage.stock_collage_specs.moulding_id:
					bullet1 = 'Framed wall art. ' + h.stock_collage.stock_collage_specs.print_medium_id.title() + ', size: ' + str(formatNumber(image_width + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2) )) + " X " + str(formatNumber(image_height + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2) )) + " inch."
				else:
					if h.stock_collage.stock_collage_specs.stretch_id:
						bullet1 = "Stretched Canvas. Canvas is wrapped over a wooden frame at the back, size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch."
						prod_details = prod_details + "Stretched Canvas: Canvas is wrapped over a wooden frame at the back. Frame is not visible from the front and sides. \n"
				prod_details = prod_details + "Canvas: Artistic matte cotton canvas 410 GSM. Matte finished, crack-resistant, water-resistant, top-coated with an ink-receptive layer. \n"
			bullet2 = ''
			if h.stock_collage.stock_collage_specs.moulding_id:
				prod_details = prod_details + "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch). Frame is made of polystyrene, which is light weight, premium finish.\n"
				incl_components = incl_components + "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch, Polystyrene). "
				bullet2 = "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch). It's a high quality frame made of Polystyrene, which is light weight, long lasting, premium finish." 
			if h.stock_collage.stock_collage_specs.mount_id:
				if h.stock_collage.stock_collage_specs.mount_size > 0:
					prod_details = prod_details + "Mount: " + str(formatNumber(h.stock_collage.stock_collage_specs.mount_size)) + " inch, Color: " + h.stock_collage.stock_collage_specs.mount.name.lower() + ", it enhances the look of this artwork. \n"
					incl_components =  incl_components + "Mount: " + str(formatNumber(h.stock_collage.stock_collage_specs.mount_size)) + " inch, Color: " + h.stock_collage.stock_collage_specs.mount.name.lower() + ". "
					bullet2 = bullet2 + ", " +str(formatNumber(h.stock_collage.stock_collage_specs.mount_size)) + " inch " + h.stock_collage.stock_collage_specs.mount.name.lower() + " mount adds classy look to this art. "

			## Total Size
			t_size_width = image_width
			t_size_height = image_height
			if h.stock_collage.stock_collage_specs.moulding:
				if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
					t_size_width = t_size_width + h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2
					t_size_height = t_size_height + h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2
			if h.stock_collage.stock_collage_specs.mount:
				t_size_width = t_size_width + h.stock_collage.stock_collage_specs.mount_size*2
				t_size_height = t_size_height + h.stock_collage.stock_collage_specs.mount_size*2
			

			t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
			prod_details = prod_details + "Product Size (with frame): " + t_size
			incl_components = incl_components + "Product Size  (with frame): " + t_size

			prod_name = "Arte'Venue framed wall art on "  + h.stock_collage.stock_collage_specs.print_medium_id.title() + "| Title: " + h.stock_image.name + " | " + t_size

			row_amz =['wallart', parent_amz_sku, "ARTE'VENUE", 
				'', '', prod_details, prod_name, '3749951031', 
				'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
				"https://artevenue.com/static/" + h.stock_collage.stock_collage_specs.display_url, qty, 
				item_total if item_total > 0 else 0.01, 									
				##Images
				img_3d_url, img_2d_url, '', '', '',
				'', '', '', '',
				
				## Variation
				variation, 'Size', '', parentage,  
					
				## Basic Info
				update_delete, h.stock_image.part_number, 'Montage Art Pvt Ltd', 
				'',
				
				## Discovery
				bullet1, bullet2, bullet3, 
				'Comes with hooks and is ready to be hung on the wall.', 
				'This is a licensed artwork. We produce museum quality art prints of this painting, frame it and deliver. Top quality, classy finish and best suited for home, office decor. Prints on canvas are as close to the original painting as it can get. Your satisfaction is guaranteed.', 
				frame_type, search_terms, color_name, packer_contact_information,
				'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
				h.stock_collage.stock_collage_specs.print_medium_id.title(), 
				'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',

				## - Diamensions
				'IN', 'IN', t_size_width, t_size_height, size_map, "Rectangle",
				'IN', 2, 'Count', 1,

				## Fulfilment
				'IN', 3, str(t_size_width + 3),
				'KG', str(t_size_height + 3), 'IN', '', 'IN', 
				'2', 
				
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
					
			wr_amz.writerow(row_amz)
			
			


			#################################################################
			#################################################################
			#################################################################
			### Child Records
			#################################################################								
			#################################################################
			#################################################################
			if h.stock_image.aspect_ratio <= 1:
				## Vertical & Square
				widths = [10, 14, 18, 24, 30]
				sq_re = "Rectangle"
			elif h.stock_image.aspect_ratio == 1:
				## Sqaure
				widths = [10, 14, 18, 24, 30]
				sq_re = "Square"
			else:
				## Horizontal
				widths = [14, 18, 24, 30, 36]
				sq_re = "Rectangle"				
								
			sku_suf = 0
			for wd in widths:
				sku_suf = sku_suf + 1
				image_width = wd
				image_height = round( wd / h.stock_image.aspect_ratio )

				mount_size = 0
				if h.stock_collage.stock_collage_specs.print_medium_id == 'CANVAS':
					mount_size = 0
				else:
					if h.stock_collage.stock_collage_specs.mount_id:
						mount_size = 1 if image_width <= 18 else 2 if image_width <= 26 else 3 if image_width <= 34 else 4							
				
				#  Get the item price
				price = get_prod_price(h.stock_image_id, 
						prod_type= h.stock_image.product_type_id,
						image_width=image_width, 
						image_height=image_height,
						print_medium_id = h.stock_collage.stock_collage_specs.print_medium_id,
						acrylic_id = h.stock_collage.stock_collage_specs.acrylic_id,
						moulding_id = h.stock_collage.stock_collage_specs.moulding_id,
						mount_size = mount_size,
						mount_id = h.stock_collage.stock_collage_specs.mount_id,
						board_id = h.stock_collage.stock_collage_specs.board_id,
						stretch_id = h.stock_collage.stock_collage_specs.stretch_id)
						
				item_total = price['item_price']
				msg = price['msg']
				cash_disc = price['cash_disc']
				percent_disc = price['percent_disc']
				item_unit_price = price['item_unit_price']
				item_disc_amt = price['disc_amt']
				disc_applied = price['disc_applied']
				promotion_id = price['promotion_id']
				# END::::    Get the item price
				#	Calculate sub total, tax for the item
				item_tax = 0
				item_sub_total = 0

				product_type_id =  h.stock_image.product_type_id

				## Increase price by 20%, to manage the returns			##################################################
				item_total = item_total + round((item_total*20/100))


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
				
			
				# 	if item price not found, return
				if item_total == 0 or item_total is None:				
					err_flg = True
					print( 'Price not available for this image ' + str(p.product_id) )
					continue
				# END:	if item price not found, don't add to cart


				length = formatNumber(image_height) 
				if h.stock_collage.stock_collage_specs.moulding:
					if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
						length = formatNumber(length + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2))
					if h.stock_collage.stock_collage_specs.mount:
						if h.stock_collage.stock_collage_specs.mount_size:
							length = formatNumber(length + (mount_size * 2))
				
				breadth = formatNumber(image_width)
				if h.stock_collage.stock_collage_specs.moulding:
					if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
						breadth = formatNumber(breadth + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2))
					if h.stock_collage.stock_collage_specs.mount:
						if h.stock_collage.stock_collage_specs.mount_size:
							breadth = formatNumber(breadth + (mount_size * 2))

				parentage = 'Child'
				variation = 'Variation'
				col = ''
				col_map = 'Multi'
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Print on ' + h.stock_collage.stock_collage_specs.print_medium_id.title()
				size_map = 'Medium'
				qty = '1000'
				update_delete = "Update"
				if image_width > h.stock_image.max_width or image_height > h.stock_image.max_height:
					update_delete = "Delete"
				
				if cat == '' or cat == 'Miscellanuous':
					prod_details = "Artwork with frame - "
				else:
					prod_details = cat + " theme artwork with frame - "
				prod_details = prod_details  + " Title: " + h.stock_image.name + ", Artist: " + h.stock_image.artist + ".\nFramed wall art. Printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + ". Licensed art print. \n"
				prod_details =  prod_details + "Print size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch. \n"
				incl_components = "One piece " + cat + " art with frame, printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + "; "
				incl_components = incl_components + "Print Size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + "; "
				if h.stock_collage.stock_collage_specs.print_medium_id == 'PAPER':
					if h.stock_collage.stock_collage_specs.moulding_id:
						bullet1 = 'Framed wall art. Licensed art print on ' + h.stock_collage.stock_collage_specs.print_medium_id.title() + ', size: ' + str(formatNumber(image_width + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2) + (mount_size *2) )) + " X " + str(formatNumber(image_height + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2) + ( mount_size * 2) )) + " inch."
					else:
						bullet1 = "Printed on " + h.stock_collage.stock_collage_specs.print_medium_id.title() + ", size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch."
					prod_details = prod_details + "Paper: Coated premium matte paper 230 GSM. Bright white, smooth finish matte, top-coated with an ink-receptive layer. \n"
				else:
					if h.stock_collage.stock_collage_specs.moulding_id:
						bullet1 = 'Framed wall art. ' + h.stock_collage.stock_collage_specs.print_medium_id.title() + ', size: ' + str(formatNumber(image_width + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2) )) + " X " + str(formatNumber(image_height + (h.stock_collage.stock_collage_specs.moulding.width_inner_inches * 2) )) + " inch."
					else:
						if h.stock_collage.stock_collage_specs.stretch_id:
							bullet1 = "Stretched Canvas. Canvas is wrapped over a wooden frame at the back, size: " + str(formatNumber(image_width)) + " X " + str(formatNumber(image_height)) + " inch."
							prod_details = prod_details + "Stretched Canvas: Canvas is wrapped over a wooden frame at the back. Frame is not visible from the front and sides. \n"
					prod_details = prod_details + "Canvas: Artistic matte cotton canvas 410 GSM. Matte finished, crack-resistant, water-resistant, top-coated with an ink-receptive layer. \n"
				bullet2 = ''
				if h.stock_collage.stock_collage_specs.moulding_id:
					prod_details = prod_details + "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch). Frame is made of polystyrene, which is light weight, premium finish.\n"
					incl_components = incl_components + "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch, Polystyrene). "
					bullet2 = "Frame: " + h.stock_collage.stock_collage_specs.moulding.name + " (" + str(formatNumber(h.stock_collage.stock_collage_specs.moulding.width_inches)) + " inch). It's a high quality frame made of Polystyrene, which is light weight, long lasting, premium finish." 
				if h.stock_collage.stock_collage_specs.mount_id :
					if h.stock_collage.stock_collage_specs.mount_size > 0:
						prod_details = prod_details + "Mount: " + str(formatNumber(mount_size)) + " inch, Color: " + h.stock_collage.stock_collage_specs.mount.name.lower() + ". Adds a decorative element within the frame. Acid free, resists aging, matte finish. \n"
						incl_components =  incl_components + "Mount: " + str(formatNumber(mount_size)) + " inch, Color: " + h.stock_collage.stock_collage_specs.mount.name.lower() + ". "
						bullet2 = bullet2 + ", " +str(formatNumber(mount_size)) + " inch " + h.stock_collage.stock_collage_specs.mount.name.lower() + ". Adds a decorative element within the frame. Acid free, resists aging, matte finish. \n"

				## Total Size
				t_size_width = image_width
				t_size_height = image_height
				if h.stock_collage.stock_collage_specs.moulding:
					if h.stock_collage.stock_collage_specs.moulding.width_inner_inches:
						t_size_width = t_size_width + h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2
						t_size_height = t_size_height + h.stock_collage.stock_collage_specs.moulding.width_inner_inches *2
				if h.stock_collage.stock_collage_specs.mount:
					t_size_width = t_size_width + mount_size*2
					t_size_height = t_size_height + mount_size*2
				
				t_size_width = round(t_size_width)
				t_size_height = round(t_size_height)
				
				'''
				if t_size_width > 27:
					continue
				if t_size_height > 27:
					continue
				'''
				
				bullet3 = ''
				if h.stock_collage.stock_collage_specs.print_medium_id == "PAPER":
					if h.stock_collage.stock_collage_specs.acrylic_id:
						prod_details = prod_details + "Paper art print covered on top with acrylic. Premium quality, clear and shatterproof. \n"
						incl_components = incl_components + "Acrylic covered; "
					bullet3 = "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility. \n"
				else:
					bullet3 = "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions. \n"

				t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
				prod_details = prod_details+ "Product Size (with frame): " + t_size
				incl_components = incl_components + "Product Size  (with frame): " + t_size

				search_terms = ( cat + " paintings, wall paintings, wall art, paintings for home decor, art print, paintings with frame, paintings for living room, paintings for bed room, wall decor " + h.stock_image.key_words.replace('|', ', '))[:150]
				
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Print on ' + h.stock_collage.stock_collage_specs.print_medium_id.title()
				qty = '100'
				
				if t_size_width == t_size_height:
					sq_re = "Square"
				else:
					sq_re = "Rectangle"
				
				prod_name = "Arte'Venue framed wall art on "  + h.stock_collage.stock_collage_specs.print_medium_id.title() + " | Title: " + h.stock_image.name + " | " + t_size

				update_delete = "Update"
				if image_width > h.stock_image.max_width or image_height > h.stock_image.max_height:
					update_delete = "Delete"
				
				finish_type = 'Matt finish'
				style_name = cat
				power_source_type = ''
				packer_contact_information = ''
				packer_contact_name = ''
				target_audience_base = ''
				length_range = ''
				importer_contact_information = ''
				frame_type = 'Polystyrene'
				theme = cat
				department = ''
				item_volume = ''
				display_volume = ''
				
				tw_size = t_size_width * t_size_height
				if tw_size <= 256:
					ship_weight = 1.5
				elif tw_size <= 576:
					ship_weight = 2
				elif tw_size <= 900:
					ship_weight = 2.5
				elif tw_size <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5
		
				item_display_weight = ship_weight


				av_sku = ("S-" + str(h.collage_id) + "-" + str(sku_suf))

				################################
				### 3D IMAGE 
				################################
				img_3d_name =  av_sku + "_3d.jpg"
				# save image
				ifile_3d = Path(img_loc + img_3d_name)
				if ifile_3d.is_file():
					print("Image already available...skipping - Main image")
				else:
					stretched_canvas = 'NO'
					if h.stock_collage.stock_collage_specs.print_medium_id == 'CANVAS' and (h.stock_collage.stock_collage_specs.moulding_id == None or h.stock_collage.stock_collage_specs.moulding_id == 0) and h.stock_collage.stock_collage_specs.stretch_id == 1:
						stretched_canvas = 'YES'

					from django.http import HttpRequest
					request = HttpRequest()
					framed_img_3d = get_FramedImage_by_id(request, h.stock_image_id, h.stock_collage.stock_collage_specs.moulding_id, 
						mount_color = h.stock_collage.stock_collage_specs.mount.color if h.stock_collage.stock_collage_specs.mount else '' , 
						mount_size=float(h.stock_collage.stock_collage_specs.mount_size) if h.stock_collage.stock_collage_specs.mount_size else 0, 
						user_width=float(image_width), prod_type=product_type_id, 
						stretched_canvas=stretched_canvas, imgtilt='YES', dropshadow='NO' )
					
					aspect_ratio = framed_img_3d.width / framed_img_3d.height

					i_width = 1200
					i_height = int(round(i_width/aspect_ratio))
					if i_height < 1000:
						i_height = 1000
						i_width = int(round(i_height * aspect_ratio))

					framed_img_3d = framed_img_3d.resize( (i_width, i_height) )				
					framed_img_3d.save(img_loc + img_3d_name)
					print("Saved: " + img_3d_name)

				
				img_3d_url = img_url + img_3d_name

				################################
				### 2D IMAGE 
				################################
				# save image
				img_2d_name =  av_sku + "_2d.jpg" 

				ifile_2d = Path(img_loc + img_2d_name)
				if ifile_2d.is_file():
					print("Image already available...skipping - Main image")
				else:
					stretched_canvas = 'NO'
					if h.stock_collage.stock_collage_specs.print_medium_id == 'CANVAS' and (h.stock_collage.stock_collage_specs.moulding_id == None or h.stock_collage.stock_collage_specs.moulding_id == 0) and h.stock_collage.stock_collage_specs.stretch_id == 1:
						stretched_canvas = 'YES'

					from django.http import HttpRequest
					request = HttpRequest()
					framed_img_2d = get_FramedImage_by_id(request, h.stock_image_id, h.stock_collage.stock_collage_specs.moulding_id, 
						mount_color = h.stock_collage.stock_collage_specs.mount.color if h.stock_collage.stock_collage_specs.mount else '' , 
						mount_size=float(h.stock_collage.stock_collage_specs.mount_size) if h.stock_collage.stock_collage_specs.mount_size else 0, 
						user_width=float(image_width), prod_type=product_type_id, 
						stretched_canvas=stretched_canvas, imgtilt='NO', dropshadow='NO' )
					
					aspect_ratio = framed_img_2d.width / framed_img_2d.height
					i_width = 1200
					i_height = int(round(i_width/aspect_ratio))
					if i_height < 1000:
						i_height = 1000
						i_width = int(round(i_height * aspect_ratio))
					
					framed_img_2d = framed_img_3d.resize( (i_width,i_height) )				
					framed_img_2d.save(img_loc + img_2d_name)				
					print("Saved: " + img_2d_name)
				
				img_2d_url = img_url + img_2d_name
					
				row_amz =['wallart', av_sku, "ARTE'VENUE", 
					'', '', prod_details, prod_name, '3749951031', 
					'India', '97020000', item_total_mrp if item_total_mrp > 0 else 0.01,
					"https://artevenue.com/static/" + h.stock_collage.stock_collage_specs.display_url, qty, 
					item_total if item_total > 0 else 0.01, 									
					##Images
					img_3d_url, img_2d_url, '', '', '',
					'', '', '', '',
					
					## Variation
					variation, 'Size', parent_amz_sku, parentage,  
						
					## Basic Info
					update_delete, h.stock_image.part_number, 'Montage Art Pvt Ltd', 
					'',
					
					## Discovery
					bullet1, bullet2, bullet3, 
					'Comes with hooks and is ready to be hung on the wall.', 
					"This is a licensed artwork. We produce high quality Giclee' prints, frame it and deliver. Premium quality wall art best suited for interiors. Your satisfaction is guaranteed.", 
					frame_type, search_terms, color_name, packer_contact_information,
					'Wall Art', theme, p_size, col_map, 'Polystyrene', '', '', 
					h.stock_collage.stock_collage_specs.print_medium_id.title(), 
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
					
				wr_amz.writerow(row_amz)

				tw_size = t_size_width * t_size_height
				if tw_size <= 256:
					ship_weight = 1.5
				elif tw_size <= 576:
					ship_weight = 2
				elif tw_size <= 900:
					ship_weight = 2.5
				elif tw_size <= 1600:
					ship_weight = 3
				else:
					ship_weight = 3.5
				
				
				row_tata = ['wallart',  '97020000', av_sku, h.stock_image.name,
						prod_name, prod_details, '', t_size_height, t_size_width, '2', ship_weight, '3', '', '',
						"ARTE'VENUE", 
						"Arte'Venue has licensed artworks from over 4,500 artists from across the world. We produce these art prints at a very high resolution with full saturation, and are fade resistant. The framing material is sourced from the best in the industry and carefully crafted using the state-of-the-art equipment. Arte'Venue was started with a vision to offer premium quality artworks at affordable prices, to the home owners, art lovers, interior designers and architects.",
						item_total, '', 'multi', '', h.stock_image_id, '', t_size, h.stock_collage.stock_collage_specs.print_medium_id.title(),
						'', '', bullet1, bullet2, bullet3, 'Comes with hooks and is ready to be hung on the wall.', 
						'Clean with a soft and dry cloth', '', cat, '', '', '', '', '',
						'Framed Art Print', 
						'', '', '', '', '', '', '', '', '', '', 
						'', '', '', '', '', '', '', '', '',
						'India', 
						'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com',
						'', '',
						"https://artevenue.com/static/" + h.stock_collage.stock_collage_specs.display_url + "\n " + img_3d_url + "\n " + img_2d_url,
						''
						]
				wr_tata.writerow(row_tata)



def generate_av_sets_feed(platform=None):
	from PIL import Image
	from PIL import ImageFont
	from PIL import ImageDraw
	import wget
	
	if env == 'PROD':
		img_loc = '/home/artevenue/website/estore/static/feeds/AV/images/'
		img_url = 'https://artevenue.com/static/feeds/AV/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		img_loc = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		img_url = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		av_url = 'https://artevenue.com/static/'
	parent_child = ''

	prod_data = {}
	
	############Common
	prod_data['hsn_code'] = '97020000'
	prod_data['brand'] = "ARTE'VENUE"
	prod_data['country_of_origin'] = "India"
	prod_data['prod_type'] = "Wall Art"
	prod_data['frame_type'] = 'Hanging'
	prod_data['frame_material'] = 'Polystyrene'
	prod_data['handling_time'] = 3
	prod_data['seller_address'] = 'Montage Art Pvt Ltd, No.165, 15th Cross, 20th Main, J.P. Nagar, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com, Bangalore 560078, Ph: 9535805505, Email: support@artevenue.com'
	
	############SKU
	prod_data['best_sellers_sku_prefix'] = 'S-'
	prod_data['sets_sku_prefix'] = 'ST-'
	prod_data['gw_sku_prefix'] = 'GW-'
	prod_data['prod_sku'] = ''

	
	############Product
	prod_data['part_number'] = ''
	prod_data['prod_name'] = prod_data['prod_desc'] = prod_data['prod_desc_for_jio'] = prod_data['prod_title'] = ''
	prod_data['prod_mrp'] = prod_data['prod_price'] = prod_data['prod_tax'] = 0 
	prod_data['quantity'] = 1000	
	prod_data['num_pieces'] = 0
	prod_data['print_surface'] = 'PAPER'
	
	############Update or delete
	prod_data['update_delete'] = 'update'
	prod_data['parent_child'] = 'C'
	
	
	############Product features, Images, Videos
	prod_data['features_1'] = prod_data['features_1_j'] = prod_data['features_2'] = prod_data['features_3'] = prod_data['features_4'] = prod_data['features_5'] = ''
	prod_data['main_image'] = prod_data['image_1'] = prod_data['image_2'] = prod_data['image_3'] = prod_data['image_5'] = ''
	prod_data['jio_main_image'] = prod_data['jio_image1'] = prod_data['jio_image2'] = prod_data['jio_image3'] = prod_data['jio_image4'] = prod_data['jio_image5'] = ''
	prod_data['dimensions_image1'] = prod_data['dimensions_image2'] = prod_data['dimensions_image3'] = prod_data['dimensions_image4'] = prod_data['dimensions_image5'] = ''
	prod_data['image_6'] = prod_data['image_7'] = prod_data['image_8'] = ''
	prod_data['jio_6'] = prod_data['jio_7'] = prod_data['jio_8'] = ''
	prod_data['video_1'] = 'https://youtu.be/6vRss_YY48I'
	prod_data['video_2'] = 'https://youtu.be/vSrersiMjWk'

	############Product Attributes
	prod_data['shape'] = ''	
	prod_data['size'] = prod_data['color_name'] = prod_data['theme'] = prod_data['search_terms'] = prod_data['jio_keywords'] = ''
	prod_data['prod_tax_percentage'] = '12%'
	prod_data['prod_condition'] = 'New'
	prod_data['parent_sku'] = ''
	
	############Product & Package Size 
	prod_data['prod_width'] = prod_data['prod_height'] = prod_data['prod_length'] = prod_data['prod_weight'] = 0
	prod_data['package_width'] = prod_data['package_height'] = prod_data['package_length'] = prod_data['package_weight'] = 0

	############Offer
	prod_data['list_price'] = prod_data['sale_price'] = 0
	prod_data['available_from_date'] = '2021-06-01'
	prod_data['sale_start_date'] = '2021-06-01'
	prod_data['sale_end_date'] = '2023-06-01'


	##############Features
	prod_data['features_1_j'] = "The best quality giclee prints produced at a very high resolution with full saturation and are fade resistant###Large format inkjet printers with archival inks are used to ensure consistent quality###Each artwork has an associated copyright and is licensed from the artist."
	prod_data['features_1'] = "The best quality giclee prints produced at a very high resolution with full saturation and are fade resistant. Large format inkjet printers with archival inks are used to ensure consistent quality. Each artwork has an associated copyright and is licensed from the artist."
	
	#########################################################################################################################
	### Create Data for Sets
	#########################################################################################################################
	sets = Stock_collage.objects.filter(is_published = True)
	if not sets:	
		print("No sets found....")
		return
		
	set_sku_int = 0
	part_number = ''
	feed = dict()
	for set in sets:
		try:
			has_specs = (set.stock_collage_specs is not None)
		except Stock_collage_specs.DoesNotExist:
			print("No spces. Skipped..." + str(set.product_id) )
			continue
			
		print("processing set..." + str(set.product_id) )
		
		image_width = 10
		image_height = round( image_width / set.aspect_ratio )
		
		if set.set_of > 1:
			sku_prefix = prod_data['sets_sku_prefix']
		else:
			sku_prefix = prod_data['best_sellers_sku_prefix']
		
		if set.set_of > 1:
			prod_name = "Framed Wall Art Set of " + str(set.set_of) + " Artworks on " + set.stock_collage_specs.print_medium_id.title()
		else:	
			prod_name = "Framed Wall Art on " + set.stock_collage_specs.print_medium_id.title()
		image_1 = set.stock_collage_specs.display_url
		
		if set.set_of > 1:
			prod_desc = "Framed wall art set titled: " + set.name + ". A set of " + str(set.set_of) + " artworks."
		else:
			prod_desc = "Framed wall art titled: "+ set.name + "."
		prod_desc_for_jio = ''
		
		if set.set_of > 1:
			search_terms = "framed wall art set, set of " + str(set.set_of) + " paintings"
			jio_keywords = "framed wall art set###set of " + str(set.set_of) + " paintings"
		else:
			search_terms = "framed wall art, framed paitings"
			jio_keywords = "framed wall art###framed paitings"

		
		items = Collage_stock_image.objects.filter(stock_collage_id = set.product_id)		
		cat = ''

		####################################################
		### Widths for the variations
		####################################################
		if set.aspect_ratio <= 1:
			## Vertical & Square
			widths = [10, 14, 18, 24, 30]
			sq_re = "Rectangle"
		elif set.aspect_ratio == 1:
			## Sqaure
			widths = [10, 14, 18, 24, 30]
			sq_re = "Square"
		else:
			## Horizontal
			widths = [14, 18, 24, 30, 36]
			sq_re = "Rectangle"				
			
		####################################################
		####################################################
		####################################################
		### Create Parent Row Data
		####################################################
		####################################################
		####################################################
		prod_data['parent_child'] = 'P'
		prod_data['num_pieces'] = set.set_of
		image_width = widths[0]
		image_height = round(image_width / set.aspect_ratio)
		print_medium_id = set.stock_collage_specs.print_medium_id
		frame_id = set.stock_collage_specs.moulding_id
		mount_id = set.stock_collage_specs.mount_id
		#mount_size = set.stock_collage_specs.mount_size
			
		prod_width = 10	## Only for the parent record, which is not variant (not for sale)
		
		############SKU
		prod_data['prod_sku'] = prod_data['sets_sku_prefix'] + str(set.product_id) + "-" + str(0)
		prod_data['parent_sku'] = prod_data['prod_sku']
		
		############Product
		prod_data['part_number'] = set.product_id
		prod_data['prod_name'] = prod_name 
		prod_data['prod_title'] = set.name
		prod_data['prod_desc'] = prod_desc
		prod_data['prod_desc_for_jio'] = prod_desc_for_jio
		prod_data['prod_mrp'] = prod_data['prod_price'] = prod_data['prod_tax'] = 100 ## Random price for the parent row 
		prod_data['quantity'] = 1
		prod_data['num_pieces'] = set.set_of
		prod_data['print_surface'] = set.stock_collage_specs.print_medium_id.title()
		
		############Update or delete
		prod_data['update_delete'] = 'update'
		
		############Product features, Images, Videos		
		if set.stock_collage_specs.print_medium_id == 'PAPER':
			prod_data['features_2'] = "Coated premium matte paper 230 GSM. Bright white, smooth finish matte, top-coated with an ink-receptive layer."
		else:
			prod_data['features_2'] = "Artistic matte cotton canvas 410 GSM which is matte finished, crack-resistant, water-resistant, and top-coated with an ink-receptive layer"
			
		prod_data['features_3'] = "Frame is made of high density polystyrene which is moisture resistant, premium finish, durable and light weight."
		prod_data['features_4'] = "All artworks are ready to hang and come with necessary hooks."
		
		prod_data['main_image'] = av_url + set.stock_collage_specs.display_url 

		#########################################################
		### MAIN IMAGE FOR JIO MART
		## Open main image
		try:
			j_file_nm =prod_data['prod_sku'].replace("-", "X") + "_1.jpg"
			j_path = Path( img_loc + j_file_nm)
			if not j_path.is_file():		
				wget.download(av_url + set.stock_collage_specs.display_url, out = img_loc + j_file_nm)
			prod_data['jio_main_image'] =  j_file_nm
		except HTTPError as e:
			continue
		#########################################################
		
		
		prod_data['image_1'] = prod_data['image_2'] = prod_data['image_3'] = prod_data['image_4'] = prod_data['image_5'] = ''

		############Product Attributes
		if set.aspect_ratio != 1:
			prod_data['shape'] = 'Rectangle'
		else:
			prod_data['shape'] = 'Square'	
										
		prod_data['size'] = str(image_width) + " X " + str(image_height) + " inch)"
		prod_data['color_name'] = ''
		prod_data['theme'] = ''		
		
		############Product & Package Size : PARENT ROW
		t_size = image_width * image_height
		if t_size <= 256:
			prod_weight = 1 * set.set_of
			ship_weight = 1.25 * set.set_of			
		elif t_size <= 576:
			prod_weight = 1.25 * set.set_of
			ship_weight = 1.5 * set.set_of			
		elif t_size <= 900:
			ship_weight = 2 * set.set_of
			prod_weight = 1.5 * set.set_of
		elif t_size <= 1600:
			prod_weight = 2.25 * set.set_of
			ship_weight = 2.75 * set.set_of
		else:
			prod_weight = 3 * set.set_of
			ship_weight = 3.5 * set.set_of

		item_display_weight = ship_weight
		prod_data['prod_width'] = image_width
		prod_data['prod_height'] = image_height
		prod_data['prod_length'] = 3		
		prod_data['package_width'] = image_width
		prod_data['package_height'] = image_height
		prod_data['package_length'] = 0
		prod_data['package_weight'] = ship_weight


		row = prod_data.copy()
		feed[str(set.product_id) + "-P"] = row

		####################################################
		####################################################
		####################################################
		### Create Child Row Data
		####################################################
		####################################################
		####################################################
		prod_data['parent_child'] = 'C'
		prod_data['num_pieces'] = set.set_of
		
		prods = Collage_stock_image.objects.filter(stock_collage_id = set.product_id)

		variant_cnt = 0
		for width in widths:		
			prod_data['image_1'] = prod_data['image_2'] = prod_data['image_3'] = prod_data['image_5'] = ''
			prod_data['jio_main_image'] = prod_data['jio_image1'] = prod_data['jio_image2'] = prod_data['jio_image3'] = prod_data['jio_image4'] = prod_data['jio_image5'] = ''
			prod_data['dimensions_image1'] = prod_data['dimensions_image2'] = prod_data['dimensions_image3'] = prod_data['dimensions_image4'] = prod_data['dimensions_image5'] = ''
			prod_data['image_6'] = prod_data['image_7'] = prod_data['image_8'] = ''
			prod_data['jio_6'] = prod_data['jio_7'] = prod_data['jio_8'] = ''
			
			image_width = width
			image_height = round(image_width / (set.aspect_ratio))

			############SKU
			variant_cnt = variant_cnt + 1
			prod_data['prod_sku'] = prod_data['sets_sku_prefix'] + str(set.product_id) + "-"  + str(variant_cnt)

			#########################################################
			### MAIN IMAGE FOR JIO MART
			## Open main image
			try:
				j_file_nm =prod_data['prod_sku'].replace("-", "X") + "_1.jpg"
				j_path = Path( img_loc + j_file_nm)
				if not j_path.is_file():		
					wget.download(av_url + set.stock_collage_specs.display_url, out = img_loc + j_file_nm)
				prod_data['jio_main_image'] =  j_file_nm
			except HTTPError as e:
				continue
			#########################################################

			
			if image_width == image_height:
				sq_re = "Square"
			else:
				sq_re = "Rectangle"
				
			if set.aspect_ratio > 1:
				mount_size = 1 if image_width <= 18 else 2 if image_width <= 26 else 3 if image_width <= 34 else 4
			else:
				mount_size = 1 if image_height <= 18 else 2 if image_height <= 26 else 3 if image_height <= 34 else 4
			
			pck_max_width = 0
			pck_max_height = 0
			_wall_area_width = 0
			prod_total = 0
			prod_sub_total = 0
			prod_tax = 0
			prod_mrp = 0
			prod_desc_for_jio = ''
			
			if set.set_of > 1:	## Reset prod desc
				prod_desc = "Framed wall art set titled: " + set.name + ". A set of " + str(set.set_of) + " artworks."  ## Reset prod desc
				prod_desc_for_jio = "It is a framed wall art set of " +  str(set.set_of) + " titled " + set.name.lower() + ". "
			else:
				prod_desc = "Framed wall art titled: " + set.name + "." 
				prod_desc_for_jio = "It is a framed wall art titled " + set.name.lower() + ". " 
			
			####################################################################
			####################################################################
			#### Gather all product data like artwork size, prod desc etc.
			####################################################################
			####################################################################
			## For JIO OINLY
			prod_desc_for_jio = prod_desc_for_jio + "Artwork(s) are printed on " + set.stock_collage_specs.print_medium_id.lower() + ", "
			if set.stock_collage_specs.moulding:
				prod_desc_for_jio = prod_desc_for_jio + "and framed with " + set.stock_collage_specs.moulding.name + " (" + str(set.stock_collage_specs.moulding.width_inches) + " inch) frame, which is made of polystyrene, has classy finish, is strong and light weight. "  if set.stock_collage_specs.moulding_id else '' 
			if set.stock_collage_specs.mount_id and set.stock_collage_specs.print_medium_id == 'PAPER' and set.stock_collage_specs.moulding:
				prod_desc_for_jio = prod_desc_for_jio + " A " + str(mount_size) + " inch, " + set.stock_collage_specs.mount.name.lower() + ' mount adds decorative element within the frame and resists aging. ' if set.stock_collage_specs.mount_id else '' 
			if not set.stock_collage_specs.moulding_id and set.stock_collage_specs.print_medium_id == 'CANVAS':
				prod_desc_for_jio = prod_desc_for_jio + "Canvas is stretched over a wooden frame at the back. Frame not visible from the front and sides. "
			
			prod_desc_for_jio = prod_desc_for_jio + "Arte'Venue has licensed artworks from over 4,500 artists from across the world. The best quality giclee art prints are produced at a very high resolution with full saturation and are fade resistant. Fine art quality paper/canvas is used with ink receptive layer. The premium framing material is sourced from the best in the industry and carefully crafted using the state-of-the-art equipment. "

			
			a_cnt = 0
			part_number = ''
			p_cnt = 0  ## Used in image generation with dimensions
			font = ImageFont.truetype("arial.ttf", 28)
			h_font = ImageFont.truetype("arial.ttf", 50)
			for p in prods:	
				a_cnt = a_cnt + 1
				product_type_id = "STOCK-IMAGE"
				if a_cnt > 1:
					part_number = part_number + ";" + p.stock_image.part_number 
				else:
					part_number = part_number + p.stock_image.part_number 
				####################################################
				#  Get the item price
				####################################################
				price = get_prod_price(p.stock_image_id, 
						prod_type = product_type_id,
						image_width=image_width, 
						image_height=image_height,
						print_medium_id = set.stock_collage_specs.print_medium_id,
						acrylic_id = set.stock_collage_specs.acrylic_id,
						moulding_id = set.stock_collage_specs.moulding_id,
						mount_size = set.stock_collage_specs.mount_size,
						mount_id = set.stock_collage_specs.mount_id,
						board_id = set.stock_collage_specs.board_id,
						stretch_id = set.stock_collage_specs.stretch_id)
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
				item_total_mrp = round( item_total + item_total * 15/100 )
			
				prod_total = prod_total + item_total
				prod_sub_total = prod_sub_total + item_sub_total
				prod_tax = prod_tax + item_tax
				prod_mrp = prod_mrp + item_total_mrp			

				#####################################################
				## Also gather data for individual products
				#####################################################
				pck_size_width = image_width
				pck_size_height = image_height

				prod_height = image_height
				prod_width = image_width
				if set.stock_collage_specs.moulding:
					if set.stock_collage_specs.moulding.width_inner_inches:
						prod_width = round(prod_width + (set.stock_collage_specs.moulding.width_inner_inches*2))
						prod_height = round(prod_height + (set.stock_collage_specs.moulding.width_inner_inches*2))
						pck_size_width = pck_size_width + (set.stock_collage_specs.moulding.width_inner_inches*2)
						pck_size_height = pck_size_height + (set.stock_collage_specs.moulding.width_inner_inches*2)
					if set.stock_collage_specs.mount and set.stock_collage_specs.print_medium_id == 'PAPER':
						if mount_size:
							prod_width = round(prod_width + (mount_size * 2))
							prod_height = round(prod_height + (mount_size * 2))
							pck_size_width = pck_size_width + (mount_size * 2)
							pck_size_height = pck_size_height + (mount_size * 2)

				if _wall_area_width == 0:
					_wall_area_width = prod_width
				else:
					_wall_area_width = _wall_area_width + prod_width + 2
				
				pck_size_width = pck_size_width + 2
				pck_size_height = pck_size_height + 2

				if pck_size_width > pck_max_width:
					pck_max_width = pck_size_width
				if pck_size_height > pck_max_height:
					pck_max_height = pck_size_height
				pck_size_length = 2 * set.set_of

				## Reinitiaze
				prod_data['features_1_j'] = "Fade-proof and best quality giclee prints produced at a very high resolution with full saturation###Large format inkjet printers with archival inks are used to ensure consistent quality###Each artwork has an associated copyright and is licensed from the artist."

				############Product & Package Size : VARIANT ROW
				t_size = prod_width * prod_height
				if t_size <= 256:
					prod_weight = 1 * set.set_of
					ship_weight = 1.25 * set.set_of
				elif t_size <= 576:
					prod_weight = 1.25 * set.set_of
					ship_weight = 1.5 * set.set_of
				elif t_size <= 900:
					prod_weight = 1.5 * set.set_of
					ship_weight = 2 * set.set_of
				elif t_size <= 1600:
					prod_weight = 2 * set.set_of
					ship_weight = 2.75 * set.set_of
				else:
					prod_weight = 2.5 * set.set_of
					ship_weight = 3.5 * set.set_of

				if set.set_of > 1:
					prod_desc = prod_desc + "\n Artwork " + str(a_cnt) + ": Finished Size " + str(prod_width) + " X " + str(prod_height) + " inches."
				else:
					prod_desc = prod_desc + "\n Finished Size: " + str(prod_width) + " X " + str(prod_height) + " inches."
					
				prod_desc = prod_desc + "\n Print Surface: " + set.stock_collage_specs.print_medium_id.title() + ". "
				prod_desc = prod_desc + "\n Print Size: " + str(image_width) + " X " + str(image_height) + " inches."
				
				if set.stock_collage_specs.moulding:
					prod_desc = prod_desc + "\nFrame: " + set.stock_collage_specs.moulding.name + " (" + str(set.stock_collage_specs.moulding.width_inches) + " inch)." if set.stock_collage_specs.moulding_id else '' 
				if set.stock_collage_specs.mount_id and set.stock_collage_specs.print_medium_id == 'PAPER' and set.stock_collage_specs.moulding:
					prod_desc = prod_desc + "\nMount: " + str(mount_size) + " inch, " + set.stock_collage_specs.mount.name.title() + "###" if set.stock_collage_specs.mount_id else ''
				if not set.stock_collage_specs.moulding_id and set.stock_collage_specs.print_medium_id == 'CANVAS':
					prod_desc = prod_desc + "\nCanvas is stretched over a wooden frame at the back. Frame not visible from the front and sides."
				search_terms = search_terms + p.stock_image.key_words			
									
				if p.stock_image.key_words:
					words = p.stock_image.key_words.replace("|", "###") 
					jio_keywords = jio_keywords + "###" + words
				

				if cat == '':
					## Get product category
					cate = Stock_image_stock_image_category.objects.filter(
					stock_image = p.stock_image).first()				
					cat = cate.stock_image_category.name.title()
					if cat.lower() == "miscellaneous" or cat.lower() ==  "miscellanuous":
						cat = 'Other'
			
			####################################################
			####################################################
			## Generate final image with dimensions
			####################################################
			####################################################
			## If it's a single image product, then image is already available
			## If it's a set, then take 1st image to be used in in the dimensions image
			'''
			if set.set_of > 1 :
				m_img_name = prod_data['prod_sku'] + "_m.jpg"
				p_img = Image.open(img_loc + "/" + prod_data['prod_sku'] + "_m1.jpg")
				wdt = p_img.width + 200
				hgt = p_img.height + 200
				im = Image.new("RGB", size = (wdt, hgt), color = (255, 255, 255))
				draw = ImageDraw.Draw(im)
				
				x = (wdt - 1100)/2				
				draw.text((x,hgt-100), '(All artworks in this set are same size)',(0,0,0),font=h_font)
				im.paste(p_img, (100, 100))
				im.save(img_loc + m_img_name)
				prod_data['dimensions_image'] = prod_data['prod_sku'] + "_m.jpg"
			else:
				prod_data['dimensions_image'] = prod_data['prod_sku'] + "_m1.jpg"
			'''
			####################################################
			####################################################
			## Get individual product images
			####################################################
			####################################################
			####################################################
			## There only 9 images that be associated on a product (1 main + 8 images)
			## Main image is already associated with the creative(room view) image
			## so, if the p_cnt exceeds 8, then skip the rest
			####################################################
			img_cnt = 0
			j_img_cnt = 0
						
			## Finish with 3d images first
			## The 3d images are first choice. 
			for p in prods:							
				img_cnt = img_cnt + 1
				j_img_cnt = img_cnt + 1
				
				if img_cnt <= 8:
					################################
					### 3D IMAGE 
					################################
					img_3d_name =  prod_data['prod_sku'] + "-" + str(img_cnt) + "_3d.jpg"
					# save image
					ifile_3d = Path(img_loc + img_3d_name)
					if ifile_3d.is_file():
						print("Image already available...skipping - Main image")
					else:
						stretched_canvas = 'NO'
						if set.stock_collage_specs.print_medium_id == 'CANVAS' and (set.stock_collage_specs.moulding_id == None or set.stock_collage_specs.moulding_id == 0) and set.stock_collage_specs.stretch_id == 1:
							stretched_canvas = 'YES'

						from django.http import HttpRequest
						request = HttpRequest()
						mnt_color = ''
						mnt_size = 0
						if set.stock_collage_specs.print_medium_id == 'PAPER':
							if set.stock_collage_specs.mount:
								mnt_color = set.stock_collage_specs.mount.color
								mnt_size = mount_size
						framed_img_3d = get_FramedImage_by_id(request, p.stock_image_id, set.stock_collage_specs.moulding_id, 
							mount_color = mnt_color, 
							mount_size=mnt_size, 
							user_width=float(image_width), prod_type='STOCK-IMAGE', 
							stretched_canvas=stretched_canvas, imgtilt='YES', dropshadow='NO' )
							
						aspect_ratio = framed_img_3d.width / framed_img_3d.height
						i_width = 1200
						i_height = int(round(i_width/aspect_ratio))
						if i_height < 1000:
							i_height = 1000
							i_width = int(round(i_height * aspect_ratio))
						
						framed_img_3d = framed_img_3d.resize( (i_width, i_height) )	
						framed_img_3d.save(img_loc + img_3d_name)
					
					################ JIO	
					jio_3d_name = prod_data['prod_sku'].replace("-","X") + "_" + str(j_img_cnt) + ".jpg"
					# save image
					ifile_3d_j = Path(img_loc + jio_3d_name)
					if ifile_3d_j.is_file():
						print("Image already available...skipping ")
					else:
						stretched_canvas = 'NO'
						if set.stock_collage_specs.print_medium_id == 'CANVAS' and (set.stock_collage_specs.moulding_id == None or set.stock_collage_specs.moulding_id == 0) and set.stock_collage_specs.stretch_id == 1:
							stretched_canvas = 'YES'

						from django.http import HttpRequest
						request = HttpRequest()
						mnt_color = ''
						mnt_size = 0
						if set.stock_collage_specs.print_medium_id == 'PAPER':
							if set.stock_collage_specs.mount:
								mnt_color = set.stock_collage_specs.mount.color
								mnt_size = mount_size
						framed_img_3d_j = get_FramedImage_by_id(request, p.stock_image_id, set.stock_collage_specs.moulding_id, 
							mount_color = mnt_color, 
							mount_size=mnt_size, 
							user_width=float(image_width), prod_type='STOCK-IMAGE', 
							stretched_canvas=stretched_canvas, imgtilt='YES', dropshadow='NO' )
							
						aspect_ratio = framed_img_3d_j.width / framed_img_3d_j.height
						i_width = 1200
						i_height = int(round(i_width/aspect_ratio))
						if i_height < 1000:
							i_height = 1000
							i_width = int(round(i_height * aspect_ratio))
						
						framed_img_3d_j = framed_img_3d_j.resize( (i_width, i_height) )				
						framed_img_3d_j.save(img_loc + jio_3d_name)
					
					img_3d_url = img_url + jio_3d_name
					_img = 'image_' + str(img_cnt)
					prod_data[_img] = img_3d_url
					prod_data["jio_image" + str(j_img_cnt)] = jio_3d_name
			
			##########################################################################
			### 2D Images, continuing img_cnt from 3d iamges above if img_cnt < 8
			###########################################################################
			for p in prods:
				if img_cnt > 8:
					break
				img_cnt = img_cnt + 1
				j_img_cnt = img_cnt + 1
				img_2d_name = prod_data['prod_sku'] + "-" + str(img_cnt) + "_2d.jpg"
				# save image
				ifile_2d = Path(img_loc + img_2d_name)
				if ifile_2d.is_file():
					print("Image already available...skipping")
				else:
					stretched_canvas = 'NO'
					if set.stock_collage_specs.print_medium_id == 'CANVAS' and (set.stock_collage_specs.moulding_id == None or set.stock_collage_specs.moulding_id == 0) and set.stock_collage_specs.stretch_id == 1:
						stretched_canvas = 'YES'

					from django.http import HttpRequest
					request = HttpRequest()
					mnt_color = ''
					mnt_size = 0
					if set.stock_collage_specs.print_medium_id == 'PAPER':
						if set.stock_collage_specs.mount:
							mnt_color = set.stock_collage_specs.mount.color
							mnt_size = mount_size
					framed_img_2d = get_FramedImage_by_id(request, p.stock_image_id, set.stock_collage_specs.moulding_id, 
						mount_color = mnt_color, 
						mount_size=mnt_size, 
						user_width=float(image_width), prod_type='STOCK-IMAGE', 
						stretched_canvas=stretched_canvas, imgtilt='NO', dropshadow='NO' )
					
					aspect_ratio = framed_img_2d.width / framed_img_2d.height
					i_width = 1200
					i_height = int(round(i_width/aspect_ratio))
					if i_height < 1000:
						i_height = 1000
						i_width = int(round(i_height * aspect_ratio))
					
					framed_img_2d = framed_img_2d.resize( (i_width, i_height) )
					framed_img_2d.save(img_loc + img_2d_name)
					
				################ JIO	
				jio_2d_name = prod_data['prod_sku'].replace("-","X") + "_" + str(j_img_cnt) + ".jpg"				
				ifile_2d_j = Path(img_loc + jio_2d_name)
				if ifile_2d_j.is_file():
					print("Image already available...skipping ")
				else:
					stretched_canvas = 'NO'
					if set.stock_collage_specs.print_medium_id == 'CANVAS' and (set.stock_collage_specs.moulding_id == None or set.stock_collage_specs.moulding_id == 0) and set.stock_collage_specs.stretch_id == 1:
						stretched_canvas = 'YES'

					from django.http import HttpRequest
					request = HttpRequest()
					mnt_color = ''
					mnt_size = 0
					if set.stock_collage_specs.print_medium_id == 'PAPER':
						if set.stock_collage_specs.mount:
							mnt_color = set.stock_collage_specs.mount.color
							mnt_size = mount_size
					framed_img_2d_j = get_FramedImage_by_id(request, p.stock_image_id, set.stock_collage_specs.moulding_id, 
						mount_color = mnt_color, 
						mount_size=mnt_size, 
						user_width=float(image_width), prod_type='STOCK-IMAGE', 
						stretched_canvas=stretched_canvas, imgtilt='NO', dropshadow='NO' )
					aspect_ratio = framed_img_2d_j.width / framed_img_2d_j.height
					i_width = 1200
					i_height = int(round(i_width/aspect_ratio))
					if i_height < 1000:
						i_height = 1000
						i_width = int(round(i_height * aspect_ratio))
					framed_img_2d_j = framed_img_2d_j.resize( (i_width, i_height) )
					framed_img_2d_j.save(img_loc + jio_2d_name)

					print("Saved: " + jio_2d_name)
				
				img_2d_url = img_url + jio_2d_name
				_img = 'image_' + str(img_cnt)
				prod_data[_img] = img_2d_url
				prod_data["jio_image" + str(j_img_cnt)] = jio_2d_name

			##########################################################################
			##########################################################################
			### Generate product Image with Measurement
			###########################################################################
			##########################################################################
			d_cnt = 0
			for p in prods:
				img_cnt = img_cnt + 1
				j_img_cnt = img_cnt + 1
				d_cnt = d_cnt + 1
				p_cnt = p_cnt+1
				jio_name_dia = prod_data['prod_sku'].replace("-","X") + "_" + str(j_img_cnt) + ".jpg"				
				img_m_name = prod_data['prod_sku'] + "_" + str(img_cnt) + ".jpg"
				
				# save image
				ifile_m = Path(img_loc + jio_name_dia)
				if ifile_m.is_file():
					prod_data['dimensions_image' + str(p_cnt)] = img_m_name
					print("Image already available...skipping")
				else:
					stretched_canvas = 'NO'
					if set.stock_collage_specs.print_medium_id == 'CANVAS' and (set.stock_collage_specs.moulding_id == None or set.stock_collage_specs.moulding_id == 0) and set.stock_collage_specs.stretch_id == 1:
						stretched_canvas = 'YES'

					from django.http import HttpRequest
					request = HttpRequest()
					mnt_color = ''
					mnt_size = 0
					if set.stock_collage_specs.print_medium_id == 'PAPER':
						if set.stock_collage_specs.mount:
							mnt_color = set.stock_collage_specs.mount.color
							mnt_size = mount_size
					framed_img_m = get_FramedImage_by_id(request, p.stock_image_id, set.stock_collage_specs.moulding_id, 
						mount_color = mnt_color, 
						mount_size=mnt_size, 
						user_width=float(image_width), prod_type='STOCK-IMAGE', 
						stretched_canvas=stretched_canvas, imgtilt='NO', dropshadow='NO' )
					
					aspect_ratio = framed_img_m.width / framed_img_m.height
					i_width = 1000
					i_height = int(round(i_width/aspect_ratio))
					if i_height < 1000:
						i_height = 1000
						i_width = int(round(i_height * aspect_ratio))
					
					framed_img_m = framed_img_m.resize( (i_width, i_height) )

					m_width = int(framed_img_m.width)
					m_height = round(framed_img_m.height)
					m_img = Image.new("RGB", size = (m_width+190, m_height+190), color = (255, 255, 255))
					m_img.paste(framed_img_m, ((25,25)))
					
					line_w_dark = Image.new(m_img.mode, (m_width, 1), 0x4E4E4E)
					line_h_dark = Image.new(m_img.mode, (1, m_height), 0x4E4E4E)
					
					## Lines
					m_img.paste(line_w_dark, ((25, m_height+25+25)))
					m_img.paste(line_h_dark, ((m_width+25+25,25)))
					
					draw = ImageDraw.Draw(m_img)
					
					## Arrow heads (triangles)
					draw.polygon([(25, m_height+25+25), (25 + 15, m_height+25+25 + 15) , (25+15, m_height+25+25 - 15)], fill=0x4E4E4E)
					draw.polygon([(m_width+25, m_height+25+25), (m_width+25 - 15, m_height+25+25 + 15) , (m_width+25 - 15, m_height+25+25 - 15)], fill=0x4E4E4E)
					
					draw.polygon([(m_width+25+25, 25), (m_width+25+25 - 15, 25 + 15) , (m_width+25+25 + 15, 25 + 15)], fill=0x4E4E4E)
					draw.polygon([(m_width+25+25, m_height+25), (m_width+25+25 - 15, m_height+25 - 15) , (m_width+25+25 + 15, m_height+25 - 15)], fill=0x4E4E4E)
					
					draw.text((int((m_width+25)/2), int(m_height+25+25+25)),str(prod_width) + '" inch',(0,0,0),font=font)
					draw.text((int(m_width+25+25+25), int((m_height+25)/2)),str(prod_height) + '" inch',(0,0,0),font=font)

					if set.set_of > 1 :
						wdt = m_img.width + 200
						hgt = m_img.height + 200
						im = Image.new("RGB", size = (wdt, hgt), color = (255, 255, 255))
						draw = ImageDraw.Draw(im)
						
						x = (wdt - 1100)/2				
						draw.text((x,hgt-100), '(All artworks in this set are same size)',(0,0,0),font=h_font)
						im.paste(m_img, (100, 100))
						im.save(img_loc + jio_name_dia)
					else:											
						m_img.save(img_loc + jio_name_dia)
						
				prod_data['dimensions_image' + str(d_cnt)] = jio_name_dia


			################################################################
			## Gather rest of the data
			################################################################
			if set.set_of > 1:
				prod_desc = prod_desc + "\nCovers approximately " + str(_wall_area_width) + " X " + str (prod_height) + " inch area on wall when hung in a single row with 2 inch gap between artworks."
				prod_size = str(prod_width) + " X " + str(prod_height) + " inch each"
			else:
				prod_size = str(prod_width) + " X " + str(prod_height) + " inch"
				
			if set.set_of > 1:
				prod_data['features_1_j'] = "Each artwork in this set is " + prod_size + "###" + prod_data['features_1_j']
			else:
				prod_data['features_1_j'] = "Finished size of this artwork is " + prod_size + "###" + prod_data['features_1_j']
				
			prod_data['part_number'] = str(set.product_id) + str(variant_cnt)
			prod_data['prod_name'] = prod_name + " | Size: " + prod_size + " | Arte'Venue" + " | Titled: " + set.name
			prod_data['prod_desc'] = prod_desc
			prod_data['prod_desc_for_jio'] = prod_desc_for_jio
			prod_data['prod_mrp'] = prod_mrp
			prod_data['prod_price'] = prod_total
			prod_data['prod_tax'] = prod_tax
			prod_data['prod_sub_total'] = prod_sub_total
			prod_data['quantity'] = 1000
			prod_data['num_pieces'] = set.set_of
			
			############Update or delete
			prod_data['update_delete'] = 'update'
			
			############Product features, Images, Videos
			prod_data['main_image'] = av_url + set.stock_collage_specs.display_url
	
			############Product Attributes
			if set.aspect_ratio != 1:
				prod_data['shape'] = 'Rectangle'
			else:
				prod_data['shape'] = 'Square'
			prod_data['size'] = prod_size
			prod_data['color_name'] = 'Multi'
			prod_data['search_terms'] = search_terms
			prod_data['jio_keywords'] = jio_keywords
			prod_data['theme'] = cat
			prod_data['part_number'] = part_number
			
			############Product & Package Size 
			prod_data['prod_width'] = prod_width
			prod_data['prod_height'] = prod_height
			prod_data['prod_length'] = 1
			prod_data['prod_weight'] = prod_weight 
			prod_data['package_width'] = pck_size_width
			prod_data['package_height'] = pck_size_height
			prod_data['package_length'] = pck_size_length
			prod_data['package_weight'] = ship_weight

			############Offer
			prod_data['list_price'] = prod_total
			prod_data['sale_price'] = prod_total
			prod_data['available_from_date'] = '2021-06-01'
			prod_data['sale_start_date'] = '2021-06-01'
			prod_data['sale_end_date'] = '2023-06-01'

			row = prod_data.copy()
			feed[str(set.product_id) + "-" + str(variant_cnt)] = row

	platform = platform.upper()
	if platform == 'JIOMART':
		generate_jiomart_feed(feed)
	elif platform == 'TATACLIQ':
		generate_tatacliq_feed(feed)
	elif platform == 'LIVSPACESTORE':
		generate_livspace_feed(feed)
	elif platform == 'LBB':
		generate_lbb_feed(feed)
	
	
def generate_tatacliq_feed(feed_data):
	if env == 'PROD':
		av_tatacliq_feed = '/home/artevenue/website/estore/static/feeds/AV/av_tatacliq_feed_1.csv'
		img_loc = '/home/artevenue/website/estore/static/feeds/AV/images/'
		img_url = 'https://artevenue.com/static/feeds/AV/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		av_tatacliq_feed = 'C:/artevenue/PRODUCT_FEEDS/AV/av_tatacliq_feed_1.csv'
		img_loc = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		img_url = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		av_url = 'https://artevenue.com/static/'
	
	with open(av_tatacliq_feed, 'w', newline='') as tatafile:
		wr_tata = csv.writer(tatafile, quoting=csv.QUOTE_ALL)
		row_tata = [ 'product_type', 'hsn_code', 'sku_code', 'title', 'name', 'description', 'ean_code', 'length', 'width',
					'height', 
					'weight', 'lead_time', 'warranty_type', 'warranty_period_months', 'brand_name', 'brand_description', 
					'mrp', 'collection_name', 'color_family', 'color', 'model_number', 'season', 'size', 'material', 'material_composition', 
					'secondary material', 'feature1', 'feature2', 'feature3', 'feature4', 'wash_care', 'care_instructions', 'pattern', 
					'battery_type', 'warranty_details', 'candle_type', 'fragrance_type', 'quantity', 'artpiece_type', 'set', 
					'set_component_name1', 'set_component1_quantity', 'set_component1_dimensions',
					'set_component_name2', 'set_component2_quantity', 'set_component2_dimensions',
					'set_component_name3', 'set_component3_quantity', 'set_component3_dimensions',
					'set_component_name4', 'set_component4_quantity', 'set_component4_dimensions',
					'set_component_name5', 'set_component5_quantity', 'set_component5_dimensions',
					'set_component_name6', 'set_component6_quantity', 'set_component6_dimensions',
					'country_of_origin', 'manufacturer', 'importer', 'packer', 
					'image_links', 'video_links', 'part_numbers'
					]
		wr_tata.writerow(row_tata)

		for prod_id, prod_data in feed_data.items():
			if prod_data['parent_child'] == 'P':
				continue
				
			row_tata = [ prod_data['prod_type'],  prod_data['hsn_code'], prod_data['prod_sku'], prod_data['prod_name'],
					prod_data['prod_name'], prod_data['prod_desc'], '', prod_data['prod_height'], 
					prod_data['prod_width'], prod_data['prod_length'], prod_data['prod_weight'] * 1000, prod_data['handling_time'], '', '',
					prod_data['brand'], 
					"Arte'Venue has licensed artworks from over 4,500 artists from across the world. We produce these art prints at a very high resolution with full saturation, and are fade resistant. The framing material is sourced from the best in the industry and carefully crafted using the state-of-the-art equipment. Arte'Venue was started with a vision to offer premium quality artworks at affordable prices, to the home owners, art lovers, interior designers and architects.",
					prod_data['prod_price'], '', prod_data['color_name'], '', prod_data['parent_sku'], '', 
					prod_data['size'], prod_data['print_surface'],
					'', '', prod_data['features_1'], prod_data['features_2'], prod_data['features_3'], prod_data['features_4'], 
					'','Clean with a soft and dry cloth',  prod_data['theme'], '', '', '', '', '',
					'Framed Art Print', 'YES' if prod_data['num_pieces'] > 1 else 'NO',
					'', '', '', '', '', '', '', '', '', '', 
					'', '', '', '', '', '', '', '',
					prod_data['country_of_origin'], 
					prod_data['seller_address'],
					'', '',
					prod_data['main_image'] + "\n " + prod_data['image_1'] + "\n " + prod_data['image_2'] + "\n " + prod_data['image_3'] + "\n " + prod_data['image_4'] + "\n " + prod_data['image_5'] + "\n " + "\n " + prod_data['image_6'] + "\n " + prod_data['image_7'] + "\n " + prod_data['image_8'],
					prod_data['video_1'] + "\n " + prod_data['video_2'], prod_data['part_number']
					]
			wr_tata.writerow(row_tata)

def generate_jiomart_feed(feed_data):
	if env == 'PROD':
		av_jiomart_feed = '/home/artevenue/website/estore/static/feeds/AV/av_jiomart_feed.csv'
		img_loc = '/home/artevenue/website/estore/static/feeds/AV/images/'
		img_url = 'https://artevenue.com/static/feeds/AV/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		av_jiomart_feed = 'C:/artevenue/PRODUCT_FEEDS/AV/av_jiomart_feed.csv'
		img_loc = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		img_url = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		av_url = 'https://artevenue.com/static/'
	
	with open(av_jiomart_feed, 'w', newline='') as jiofile:
		wr_jio = csv.writer(jiofile, quoting=csv.QUOTE_ALL)
		row_tata = [ 'category name', 'category_id', 'product_code', 'title', 'description', 'brand',
					'model', 'image groups', 
					
					'product image 1', 'product image 2', 'product image 3', 'product image 4', 'product image 5', 
					'legal image 1', 'legal image 2', 'legal image 3', 'legal image 4', 'legal image 5', 
					
					'hsn', 'tax rate', 	
					
					'web url link', 'keywords', 'key features', 'manufacturing address code', 
					
					'importers', 'marketed by', 'food cupon accepted', 'weighted item', 'disclaimer',
					
					'box contents', 'care instructions', 'safety warning', 'safety rating',
					
					'variant sku', 'variant title', 'variant images', 'variant default_image', 'ean', 'stock sku', 'vendor',
					
					'price type', 'MRP', 'offer price', 
					
					'discount slab 1 range', 'discout slab 1 type', 'discount slab 1 discount', 
					'discount slab 2 range', 'discout slab 2 type', 'discount slab 2 discount', 
					'discount slab 3 range', 'discout slab 3 type', 'discount slab 3 discount', 
					'minimum order quantity', 'maximum order quantity', 'warranty', 'inventory sku',
					
					'fulfiller branch number', 'batch number', 'available quantity', 
					'multiplier', 'low stock threshold', 'min lead time to source',
					'max lead time to source', 'lead time unit', 'min time to ship', 'max time to ship', 
					'shipping time unit', 'shelf life value', 'shelf life unit', 'shipping zone code',
					'shipping cost', 
					
					
					'country of origin', 'notes', 'best before buy date', 'manufactored date',
					'month year of import', 
					
					'item dimensions length value', 'item dimensions length unit', 
					'item dimensions width value', 'item dimensions widht unit', 
					'item dimensions height value', 'item dimensions height unit', 
					'item dimensions depth value', 'item dimensions depth unit', 
					'item dimensions net weight value', 'item dimensions net weight unit',
					'item dimensions volume value', 'item dimensions volume unit',
					
					'package dimensions length value', 'package dimensions length unit', 
					'package dimensions width value', 'package dimensions widht unit', 
					'package dimensions height value', 'package dimensions height unit', 
					'package dimensions depth value', 'package dimensions depth unit', 
					'package dimensions gross weight value', 'package dimensions gross weight unit',
					'package dimensions volumetric weight value', 'package dimensions volumetric weight unit',
					
					'size', 'color', 'match', 'pivot', 'shape', 'sty;e', 'theme', 'finish', 'blacklit',
					'pack of', 'fogfree', 'material', 'turntable', 'washable', 'character', 'ideal for',
					'ideal use', 'laminated', 'mechanism', 'case color', 'clock type', 'dial color', 'dial shape',					
					
					'extendable', 'how to use', 'magnifying', 'mount type', 'paper type', 'print type',
					'sound type', 'wall amount', 'water proof', 'with glass', 'mirror type', 'battery type',
					'flamability', 'hour markers', 'luxury clock', 'mirror shape', 'power source', 'printed text', 
					
					'product type', 'sticker type', 'suitable for', 'vehicle type', 'bevelled edge', 'dial material',
					'diameter', 'god idol type', 'magnification', 'number of led', 'self adhesive', 'sticker shape',
					'ideal location', 'transporation', 'lamination type', 'luxury material', 'mount mechanism', 'number of hands',
					
					'water resistant', 'application type', 'framed/frameless', 'storage category', 'display size',
					'finish width', 'scratch resistant', 'scratch-resistant', 'dial diameter', 'finish height', 'hazardous material',
					'case bezel material', 'number of batteries', 'paper desity', 'area covered', 'power requirement',
					
					'number of cabinate doors', 'showpiece figurine type', 'nuber of cabinate shelves', 
					'hazardous material - type1', 'hazardous material - type2', 'showpiece figurine sub-type',
					'storage temp limit', 
					]
		wr_jio.writerow(row_tata)

		for prod_id, prod_data in feed_data.items():
			if prod_data['parent_child'] == 'P':
				continue
			prod_sku = prod_data['prod_sku'].replace('-', 'X')
			
			if prod_data['num_pieces'] > 1:
				prod_name = prod_data['brand'] + " " + prod_data['prod_title'] +  " Framed Wall Art " + str(prod_data['prod_width']) + " X " + str(prod_data['prod_height']) + " inch" + " (set of " + str(prod_data['num_pieces']) + ")"
			else:
				prod_name = prod_data['brand'] + " " + prod_data['prod_title'] + " " + " Framed Wall Art on " + str(prod_data['print_surface']) +   " " + str(prod_data['prod_width']) + " X " + str(prod_data['prod_height']) + " inch"

			import re
			prod_data['jio_keywords'] = re.sub(r'\SKU:\d*\b', '', prod_data['jio_keywords'])
			
			
			if prod_data['prod_price'] >= 30000:
				continue
			'''
			## Process main image to add white background around it
			img_source = Image.open(img_loc+prod_data['jio_main_image'])
			r = img_source.width / img_source.height
			width = int(img_source.width + (img_source.width*2/100))
			height = round(width / r)
			img = Image.new("RGB", size = (width, height), color = (255, 255, 255))
			halfwidth = int((img_source.width*2/100) / 2)
			img.paste(img_source, ((halfwidth,halfwidth)))
			img_name = prod_sku + "_1.jpg"
			img.save(img_loc + img_name)							
			prod_data['jio_main_image']	= img_loc + img_name
			'''

			row_tata = [ 'Wall Decor', 'home_groc_home_home_wall', prod_sku, prod_name, prod_data['prod_desc_for_jio'], 
						"ARTE'VENUE", prod_data['parent_sku'], 'Product Images###Legal Images',
						
						prod_data['jio_main_image'], prod_data['jio_image2'], prod_data['jio_image3'], prod_data['jio_image4'], prod_data['jio_image5'], 
						prod_data['dimensions_image1'], prod_data['dimensions_image2'], prod_data['dimensions_image3'], prod_data['dimensions_image4'], prod_data['dimensions_image5'],	
						
						prod_data['hsn_code'], '', '', prod_data['jio_keywords'], 
						prod_data['features_1_j'] + "###" + prod_data['features_2'] + "###" + prod_data['features_3'] + "###" + prod_data['features_4'],
						'aa60ca49232deaf7857a33af88a66fd8', '', 'MONTAGE ART PRIVATE LIMITED', 'FALSE', 'FALSE', '',

						
						##'box contents', 'care instructions', 'safety warning', 'safety rating',
						str(prod_data['num_pieces']) + ' piece wall art', 'Wipe with clean, dry and soft cloth', '', '',
						
						
						##'variant sku', 'variant title', 'variant images', 'variant default_image', 'ean', 'stock sku', 'vendor',
						prod_sku, prod_name, '', '', '', prod_sku, '',
						
						
						##'price type', 'MRP', 'offer price', 
						'M Type', prod_data['prod_mrp'], prod_data['prod_price'],
						

						##'discount slab 1 range', 'discout slab 1 type', 'discount slab 1 discount', 
						##'discount slab 2 range', 'discout slab 2 type', 'discount slab 2 discount', 
						##'discount slab 3 range', 'discout slab 3 type', 'discount slab 3 discount', 
						'', '', '', 
						'', '', '', 
						'', '', '', 
						
						##'minimum order quantity', 'maximum order quantity', 'warranty', 'inventory sku',
						'1', '100', '', prod_sku,
						
						##'fulfiller branch number', 'batch number', 'available quantity', 
						##'multiplier', 'low stock threshold', 'min lead time to source',
						##'max lead time to source', 'lead time unit', 'min time to ship', 'max time to ship', 
						##'shipping time unit', 'shelf life value', 'shelf life unit', 'shipping zone code',
						##'shipping cost', 
						'3PEOWMEW669', '', '100', '1', '5', '1', '3', 'days',
						'1', '3', 'days', '0', 'days', '648ec88c630208c5fde0dceee41ea27494087860',
						'0',

						
						##'country of origin', 'notes', 'best before buy date', 'manufactored date',
						##'month year of import', 
						'INDIA', '', '', '', '',
						

						##'item dimensions length value', 'item dimensions length unit', 
						##'item dimensions width value', 'item dimensions widht unit', 
						##'item dimensions height value', 'item dimensions height unit', 
						##'item dimensions depth value', 'item dimensions depth unit', 
						##'item dimensions net weight value', 'item dimensions net weight unit',
						##'item dimensions volume value', 'item dimensions volume unit',
						float(prod_data['prod_length'])*2.54, 'centimeter', float(prod_data['prod_width'])*2.54, 'centimeter', 
						float(prod_data['prod_height']*2.54), 'centimeter', '', '', 
						prod_data['prod_weight'], 'kilogram', 
						'', '',	

						##'package dimensions length value', 'package dimensions length unit', 
						##'package dimensions width value', 'package dimensions widht unit', 
						##'package dimensions height value', 'package dimensions height unit', 
						##'package dimensions depth value', 'package dimensions depth unit', 
						##'package dimensions gross weight value', 'package dimensions gross weight unit',
						##'package dimensions volumetric weight value', 'package dimensions volumetric weight unit',
						float(prod_data['package_length'])*2.54, 'centimeter', float(prod_data['package_width'])*2.54, 'centimeter',
						float(prod_data['package_height'])*2.54, 'centimeter', '', '',
						prod_data['package_weight'], 'kilogram',						
						float(prod_data['package_length'])* 2.54 * float(prod_data['package_width'])* 2.54 * float(prod_data['package_height'])* 2.54 / 5000, 'kilogram',

						##'size', 'color', 'match', 'pivot', 'shape', 'style', 'theme', 'finish', 'blacklit',
						##'pack of', 'fogfree', 'material', 'turntable', 'washable', 'character', 'ideal for',
						##'ideal use', 'laminated', 'mechanism', 'case color', 'clock type', 'dial color', 'dial shape',					
						'', 'Multicolor', '', 'false', prod_data['shape'], '', prod_data['theme'], 'Matte', 'false',
						prod_data['num_pieces'], 'false', prod_data['print_surface'].title(), 'false', 'false', '', '',
						'', 'false', '', '', '', '', '',

						##'extendable', 'how to use', 'magnifying', 'mount type', 'paper type', 'print type',
						##'sound type', 'wall amount', 'water proof', 'with glass', 'mirror type', 'battery type',
						##'flamability', 'hour markers', 'luxury clock', 'mirror shape', 'power source', 'printed text', 
						'false', '', 'false', 'Wall Mount', '', '',
						'', 'true', 'false', 'false', '', '',
						'Not Flammable', '', 'false', '', '', 'false',
						
						##'product type', 'sticker type', 'suitable for', 'vehicle type', 'bevelled edge', 'dial material',
						##'diameter', 'god idol type', 'magnification', 'number of led', 'self adhesive', 'sticker shape',
						##'ideal location', 'transporation', 'lamination type', 'mount mechanism', 'number of hands',
						'Wall Decor & Hanging', '', '', '', 'false', '',
						'', 'NA', '', '', 'false', '', 
						'', 'General Transport', '', '', 'Wall Mounted', '',
						
						
						##'water resistant', 'application type', 'framed/frameless', 'storage category', 'display size',
						##'finish width', 'scratch resistant', 'scratch-resistant', 'dial diameter', 'finish height', 'hazardous material',
						##'case bezel material', 'number of batteries', 'paper desity', 'area covered', 'power requirement',
						'false', '', 'Framed', 'Normal Storage', '',
						'', 'false', 'false', '', '', 'false', 
						'', '', '', '' , '',   ##float(prod_data['package_length'])* 0.083333 * float(prod_data['package_width'])* 0.083333 * float(prod_data['package_height'])* 0.083333 


						##'number of cabinate doors', 'showpiece figurine type', 'nuber of cabinate shelves', 
						##'hazardous material - type1', 'hazardous material - type2', 'showpiece figurine sub-type',
						##'storage temp limit', 
						'', '', '',
						'', '', '', 
						'Normal Warehouse Temperature'					
					]
			wr_jio.writerow(row_tata)


def generate_livspace_feed(feed_data):
	if env == 'PROD':
		av_single_img_file = '/home/artevenue/website/estore/static/feeds/livspacestore/single_img_prod_input.csv'
		av_set_file = '/home/artevenue/website/estore/static/feeds/livspacestore/set_input.csv'
		av_gw_file = '/home/artevenue/website/estore/static/feeds/livspacestore/gw_input.csv'
		av_livspace_feed = '/home/artevenue/website/estore/static/feeds/livspacestore/av_livspace_feed.csv'
		img_url = 'https://artevenue.com/static/feeds/livspacestore/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		av_single_img_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/single_img_prod_input.csv'
		av_set_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/set_input.csv'
		av_gw_file = 'C:/artevenue/PRODUCT_FEEDS/livspacestore//gw_input.csv'
		av_livspace_feed = 'C:/artevenue/PRODUCT_FEEDS/livspacestore/av_livspace_feed.csv'
		av_url = 'https://artevenue.com/static/'


	with open(av_livspace_feed, 'w', newline='') as livfile:
		wr_livspace = csv.writer(livfile, quoting=csv.QUOTE_ALL)
		row =["product_type", "artevenue_sku", 'brand', 'product_id', 'product_type',
			'product_description', 'product_title', 'country_of_origin', 'HSN_Code',
			'Maximum Retail Price(incl GST)', 'Main Image URL', 
			'Quantity', 			
			'Other Image URL1', 'Other Image URL2', 'Other Image URL3', 'Other Image URL4', 'Other Image URL5', 
			## Variation

			## Basic Info
			'update_delete', 'manufacturer',

			## Discovery
			'bullet_point1', 'bullet_point2', 'bullet_point3',
			'bullet_point4', 'bullet_poin5', 'frame_type', 'theme', 'size', 'search_terms',
			
			## Dimensions
			'Item Width Unit of Measure', 'Item Height Unit of Measure', 'Item Width', 
			'Item Height', 'Shape', 'Item Length Unit of Measure', 
			'Item Length', 'Unit Count Type', 'Unit Count',
			
			## Fulfilment
			'Package Height Unit of Measure', 'Package Length', 'Package Width',
			'Package Weight Unit of Measure', 'Package Height', 'Package Width Unit of Measure',
			'Package Length Unit of Measure', 'Package Weight',
			
			## Offer
			'Offer Start Date', 'Offer End Date', 'Currency', 'Max Order Quantity',
			'GST %', 'Shipping Time', 'Delivery Time',
			'Condition', 'Sale Price(incl GST)', 
			'Sale Start Date', 'Sale End Date'
		]

		wr_livspace.writerow(row)


		for prod_id, prod_data in feed_data.items():
			if prod_data['parent_child'] == 'P':
				continue
			row =[ prod_data['prod_type'], prod_data['prod_sku'], prod_data['brand'], 
				prod_data['part_number'], 'Framed Artwork',
				prod_data['prod_desc'], prod_data['prod_name'], prod_data['country_of_origin'], prod_data['hsn_code'], 
				prod_data['prod_mrp'], prod_data['main_image'], 
				prod_data['quantity'], 
				
				##Images
				prod_data['image_1'], prod_data['image_2'], prod_data['image_3'], prod_data['image_4'], prod_data['image_5'],
				######img_3d_url, img_2d_url, '', '', '',

				## Variation
					
				## Basic Info
				prod_data['update_delete'], 'Montage Art Pvt Ltd', 
				
				## Discovery
				prod_data['features_1'], prod_data['features_2'], prod_data['features_3'], prod_data['features_4'],
				'', 
				prod_data['frame_material'], prod_data['theme'], prod_data['size'], prod_data['search_terms'], 

				## - Diamensions
				'IN', 'IN', prod_data['prod_width'], prod_data['prod_height'], prod_data['shape'],
				'IN', 2, 'Count', 1,

				## Fulfilment
				'IN', 3, prod_data['package_width'], 'KG', prod_data['package_height'], 'IN', 'IN', prod_data['prod_weight'], 
				
				##-- Offer
				prod_data['available_from_date'], '12-31-2022',  'INR', 100, 
				'12%', prod_data['handling_time'], 
				'Delivered by courier to most cities in India in 4-7 days', 
				'New', prod_data['prod_price'], 
				prod_data['sale_start_date'], prod_data['sale_end_date'],
				]
				
			wr_livspace.writerow(row)


'''
def genreate_google_feed(feed_data):

			#id	title	description	link	image_link	additional_image_link	availability	availability_​​date	
			#expiration_​​date	price	
			#google_​​product_​​category	product_type	brand	gtin	MPN	material	size	item_group_id	
			#product_length	product_width	product_height	product_weight	product_detail	product_highlight	
			#custom_label_0	custom_label_1	custom_label_2	custom_label_3	custom_label_4	promotion_​​id				
			#shipping	ships_from_country	max_handling_time
			
	if env == 'PROD':
		google_file_nm = '/home/artevenue/website/estore/static/feeds/google/av_google_feed.csv'

		img_url = 'https://artevenue.com/static/feeds/google/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		google_file_nm = 'C:/artevenue/PRODUCT_FEEDS/google/av_google_feed.csv'
		img_url = 'C:/artevenue/PRODUCT_FEEDS/google/images/'
		av_url = 'https://artevenue.com/static/'
	
	with open(google_file_nm, 'w', newline='') as file:
		wr_g = csv.writer(file, quoting=csv.QUOTE_ALL)
		row = [ 'id', 'title', 'description', 'link', 'image_link', 'availability',
					'availability_date', 'expiration_date', 'price', 'google_​​product_​​category',
					'product_type', 'brand', 'gtin', 'MPN', 'material', 'size', 'item_group_id',
					'product_length', 'product_width', 'product_height', 'product_weight', 
					'product_detail', 'product_highlight', 'custom_label_0', 'custom_label_1',
					'custom_label_2', 'custom_label_3', 'custom_label_4', 'promotion_​​id',
					'shipping', 'ships_from_country', 'max_handling_time'
					]
		wr_g.writerow(row_tata)

		for prod_id, prod_data in feed_data.items():
			if prod_data['parent_child'] == 'P':
				continue
			
			if prod_data['num_pieces'] > 1:
				prod_name = prod_data['brand'] + " " + prod_data['prod_title'] + " " + prod_data['print_surface'] + " framed wall art " + str(prod_data['prod_width']) + " X " + str(prod_data['prod_height']) + " inch" + " (set of " + str(prod_data['num_pieces']) + ")"
			else:
				prod_name = prod_data['brand'] + " " + prod_data['prod_title'] + " framed wall art on " + str(prod_data['print_surface']) + " (" + str(prod_data['prod_width']) + " X " + str(prod_data['prod_height']) + " inch)"

			row = [ ,prod_data['prod_title'],
			
	
			row_tata = [ 'Wall Decor', 'home_groc_home_home_wall', prod_sku, prod_name, prod_data['prod_desc_for_jio'], 
						"ARTE'VENUE", prod_data['parent_sku'], 'Product Images###Legal Images',
						
						prod_data['jio_main_image'], prod_data['jio_image2'], prod_data['jio_image3'], prod_data['jio_image4'], prod_data['jio_image5'], 
						prod_data['dimensions_image1'], prod_data['dimensions_image2'], prod_data['dimensions_image3'], prod_data['dimensions_image4'], prod_data['dimensions_image5'],
						
						
						prod_data['hsn_code'], '', '', prod_data['jio_keywords'], 
						prod_data['features_1_j'] + "###" + prod_data['features_2'] + "###" + prod_data['features_3'] + "###" + prod_data['features_4'],
						'aa60ca49232deaf7857a33af88a66fd8', '', 'MONTAGE ART PRIVATE LIMITED', 'FALSE', 'FALSE', '',

						
						##'box contents', 'care instructions', 'safety warning', 'safety rating',
						str(prod_data['num_pieces']) + ' piece wall art', 'Wipe with clean, dry and soft cloth', '', '',
						
						
						##'variant sku', 'variant title', 'variant images', 'variant default_image', 'ean', 'stock sku', 'vendor',
						prod_sku, prod_name, '', '', '', prod_sku, '',
						
						
						##'price type', 'MRP', 'offer price', 
						'M Type', prod_data['prod_mrp'], prod_data['prod_price'],
						

						##'discount slab 1 range', 'discout slab 1 type', 'discount slab 1 discount', 
						##'discount slab 2 range', 'discout slab 2 type', 'discount slab 2 discount', 
						##'discount slab 3 range', 'discout slab 3 type', 'discount slab 3 discount', 
						'', '', '', 
						'', '', '', 
						'', '', '', 
						
						##'minimum order quantity', 'maximum order quantity', 'warranty', 'inventory sku',
						'1', '100', '', prod_sku,
						
						##'fulfiller branch number', 'batch number', 'available quantity', 
						##'multiplier', 'low stock threshold', 'min lead time to source',
						##'max lead time to source', 'lead time unit', 'min time to ship', 'max time to ship', 
						##'shipping time unit', 'shelf life value', 'shelf life unit', 'shipping zone code',
						##'shipping cost', 
						'3PEOWMEW669', '', '100', '1', '5', '1', '3', 'days',
						'1', '3', 'days', '0', 'days', '0e4295d0ed8e4f09b4b5a18ab9c9e4c799fca18d',
						'0',

						
						##'country of origin', 'notes', 'best before buy date', 'manufactored date',
						##'month year of import', 
						'INDIA', '', '', '', '',
						

						##'item dimensions length value', 'item dimensions length unit', 
						##'item dimensions width value', 'item dimensions widht unit', 
						##'item dimensions height value', 'item dimensions height unit', 
						##'item dimensions depth value', 'item dimensions depth unit', 
						##'item dimensions net weight value', 'item dimensions net weight unit',
						##'item dimensions volume value', 'item dimensions volume unit',
						float(prod_data['prod_length'])*2.54, 'centimeter', float(prod_data['prod_width'])*2.54, 'centimeter', 
						float(prod_data['prod_height']*2.54), 'centimeter', '', '', 
						prod_data['prod_weight'], 'kilogram', '', '',
						


						##'package dimensions length value', 'package dimensions length unit', 
						##'package dimensions width value', 'package dimensions widht unit', 
						##'package dimensions height value', 'package dimensions height unit', 
						##'package dimensions depth value', 'package dimensions depth unit', 
						##'package dimensions gross weight value', 'package dimensions gross weight unit',
						##'package dimensions volumetric weight value', 'package dimensions volumetric weight unit',
						float(prod_data['package_length'])*2.54, 'centimeter', float(prod_data['package_width'])*2.54, 'centimeter',
						float(prod_data['package_height'])*2.54, 'centimeter', '', '',
						prod_data['package_weight'], 'kilogram',						
						float(prod_data['package_length'])* 2.54 * float(prod_data['package_width'])* 2.54 * float(prod_data['package_height'])* 2.54 / 5000, 'kilogram',

						##'size', 'color', 'match', 'pivot', 'shape', 'style', 'theme', 'finish', 'blacklit',
						##'pack of', 'fogfree', 'material', 'turntable', 'washable', 'character', 'ideal for',
						##'ideal use', 'laminated', 'mechanism', 'case color', 'clock type', 'dial color', 'dial shape',					
						'', 'Multicolor', '', 'false', prod_data['shape'], '', prod_data['theme'], 'Matte', 'false',
						prod_data['num_pieces'], 'false', prod_data['print_surface'].title(), 'false', 'false', '', '',
						'', 'false', '', '', '', '', '',

						##'extendable', 'how to use', 'magnifying', 'mount type', 'paper type', 'print type',
						##'sound type', 'wall amount', 'water proof', 'with glass', 'mirror type', 'battery type',
						##'flamability', 'hour markers', 'luxury clock', 'mirror shape', 'power source', 'printed text', 
						'false', '', 'false', 'Wall Mount', '', '',
						'', 'true', 'false', 'false', '', '',
						'Not Flammable', '', 'false', '', '', 'false',
						
						##'product type', 'sticker type', 'suitable for', 'vehicle type', 'bevelled edge', 'dial material',
						##'diameter', 'god idol type', 'magnification', 'number of led', 'self adhesive', 'sticker shape',
						##'ideal location', 'transporation', 'lamination type', 'mount mechanism', 'number of hands',
						'Wall Decor & Hanging', '', '', '', 'false', '',
						'', 'NA', '', '', 'false', '', 
						'', 'General Transport', '', '', 'Wall Mounted', '',
						
						
						##'water resistant', 'application type', 'framed/frameless', 'storage category', 'display size',
						##'finish width', 'scratch resistant', 'scratch-resistant', 'dial diameter', 'finish height', 'hazardous material',
						##'case bezel material', 'number of batteries', 'paper desity', 'area covered', 'power requirement',
						'false', '', 'Framed', 'Normal Storage', '',
						'', 'false', 'false', '', '', 'false', 
						'', '', '', '' , '',   ##float(prod_data['package_length'])* 0.083333 * float(prod_data['package_width'])* 0.083333 * float(prod_data['package_height'])* 0.083333 


						##'number of cabinate doors', 'showpiece figurine type', 'nuber of cabinate shelves', 
						##'hazardous material - type1', 'hazardous material - type2', 'showpiece figurine sub-type',
						##'storage temp limit', 
						'', '', '',
						'', '', '', 
						'Normal Warehouse Temperature'					
					]
			wr_jio.writerow(row_tata)



'''

def generate_lbb_feed(feed_data):

			
	if env == 'PROD':
		av_lbb_feed = '/home/artevenue/website/estore/static/feeds/AV/av_lbb_feed.csv'
		img_loc = '/home/artevenue/website/estore/static/feeds/AV/images/'
		img_url = 'https://artevenue.com/static/feeds/AV/images/'
		av_url = 'https://artevenue.com/static/'
	else:
		av_lbb_feed = 'C:/artevenue/PRODUCT_FEEDS/AV/av_lbb_feed.csv'
		img_loc = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		img_url = 'C:/artevenue/PRODUCT_FEEDS/AV/images/'
		av_url = 'https://artevenue.com/static/'


	with open(av_lbb_feed, 'w', newline='') as lbbfile:
		wr_lbb = csv.writer(lbbfile, quoting=csv.QUOTE_ALL)
			
		header_row = ['Brand', 'Name of Product', 'MRP', 'Selling Price', 'GST', 'Inventory', 'Material', 
				'Package Contents', 'Weight in gms', 'Dimension Unit', 'Product Length', 'Product Breadth', 'Product Height',
				'Product Diameter', 'Shipping Time', 'Fragile', 'Lead Free (Yes/No)', 'Merchant SKU Code', 'USP',
				'Wall Decor Type', 'Box Contents', 'HSN Code']
		wr_lbb.writerow(header_row)

		for prod_id, prod_data in feed_data.items():
			if prod_data['parent_child'] == 'P':
				continue
			
			if prod_data['num_pieces'] > 1:
				prod_name = "Framed Wall Art on " + prod_data['print_surface'] + ", Titled: " + prod_data['prod_title'] +  " | " + " Set of " + str(prod_data['num_pieces']) + " | " + str(prod_data['prod_width']) + " X " + str(prod_data['prod_height']) + " inch each"  
			else:
				prod_name = "Framed Wall Art on "  + prod_data['print_surface'] +  ", Titled: " + prod_data['prod_title'] + " | " + str(prod_data['prod_width']) + " X " + str(prod_data['prod_height']) + " inch"
				
			row = [ prod_data['brand'], prod_name, prod_data['prod_mrp'], prod_data['prod_price'], prod_data['prod_tax'], '500', prod_data['print_surface'], 
				str(prod_data['num_pieces']) + ' artwork(s)', prod_data['prod_weight'] * 1000, 'inch', prod_data['prod_length'], prod_data['prod_width'], prod_data['prod_height'],
				'', '1-3 Days', 'Yes', 'Yes', prod_data['prod_sku'], prod_data['features_1'] + " " + prod_data['features_3'] + " " + prod_data['features_4'], 
				'Wall Art', str(prod_data['num_pieces']) + ' artwork(s)', prod_data['hsn_code'],
				prod_data['main_image'], prod_data['image_1'], prod_data['image_2'], prod_data['image_3'], prod_data['image_4'], prod_data['image_5'], prod_data['image_6'], prod_data['image_7'], prod_data['image_8']
			]
			wr_lbb.writerow(row)

			
				
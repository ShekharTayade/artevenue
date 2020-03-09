from artevenue.models import Product_view, Moulding, Moulding_image
from artevenue.models import Curated_collection, Mount
from artevenue.models import Stock_image, Stock_image_stock_image_category
from channelsales.models import Montage_amz_data
from django.conf import settings
from decimal import Decimal

from PIL import Image, ImageFilter, ImageFile
import requests
import csv

from artevenue.views.product_views import *
from artevenue.views.tax_views import *
from artevenue.views.price_views import *
from artevenue.views.image_views import *

import requests
from io import BytesIO

ImageFile.LOAD_TRUNCATED_IMAGES = True


def amazon_data():


	##curated = Curated_collection.objects.filter(curated_category_id = 4) ## for Kids
	curated = Curated_collection.objects.filter(curated_category_id = 9) ## for Vintage
	createAmazonData(curated)

def createAmazonData(curated):
	
	cnt = 0
	sku_suf = "AV"
	##sku_int = 550000  ## for Kids	
	sku_int = 560000  ## for Vintage
	
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
		hl = Montage_amz_data(
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
			quantity = 0,
			item_unit_price = 0,
			item_sub_total = 0,
			item_disc_amt  = 0,
			item_tax  = 0,
			item_total = 0,
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
			image_width = 0,
			image_height = 0,
			created_date = today,
			updated_date = today,
			parent_child = 'P',
			parent_amz_sku = ''
		)
		hl.save()		
		

		
		#########################################################
		## Create 5 versions with different sizes
		#########################################################
		sizes = [12, 18, 24, 30, 36]

		for size in sizes:		
			if prod.orientation == 'Vertical' or prod.orientation == 'Square':
				img_width = size
				img_height = round(img_width / prod.aspect_ratio)
			else:
				img_height = size
				img_width = round(img_height * prod.aspect_ratio)			

			moulding_id = 18 # Simple Black
				
			
			moulding = Moulding.objects.get( moulding_id = moulding_id )
			moulding_name = ''
			if moulding:
				moulding_name = moulding.name

			mount = Mount.objects.get(pk=3)   ## Offwhite
			mount_color = ''
			if mount :
				mount_color = mount.color
		
			if size == 12 or size == 24:
				mount_size = 1
			else:
				mount_size = 2
				
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
			# Generate Amazon SKU Number
			#####################################################
			sku_int = sku_int + 1
			amz_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Amazon SKU Number
			#####################################################
			
			'''
			if size == 12:
				parent_child = "P"
				parent_sku = amz_sku
			else:
				parent_child = "C"
			'''
			
			#####################################################
			# Create Amazon DATA
			#####################################################
			## Insert or Update
			promo_name = ''
			if promotion:
				promo_name = promotion.name
			hl = Montage_amz_data(
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


	
	print("Data creation/Update complete: Count - " + str(cnt) )

def createAmazonImages():	
	##amazon_data = Amazon_data.objects.filter(amazon_key__gt = 27478,
	##	amazon_sku__gte = 'AV515936').order_by('amazon_key')  ##Kids
	##amazon_data = Amazon_data.objects.filter(amazon_sku__gte = 'AV560000').order_by('amazon_key')  ## Vintage
	
	## amazon_data = Amazon_data.objects.filter(amazon_sku__gte = 'AVC10001').order_by('amazon_key')  ## Landscape - Campaigns
	#amazon_data = Amazon_data.objects.filter(amazon_key__gte = 35319).order_by('amazon_key')  ## Floral - Campaigns

	abstract_ids = [119513,193908,87845,47869,36120,238888,255004,195569,240176,78373,80171,262895,263713,218461,280822]
	amazon_data = Montage_amz_data.objects.filter(product_id__in = abstract_ids
		, amazon_sku__startswith = 'MNCA').order_by('amazon_key')  ## Abstract - Campaigns
	
	for h in amazon_data:
		if h.parent_child == 'P':
			image_width = 16
		else:
			image_width = h.image_width
	
		if h.moulding:
			if h.mount:
				framed_img = get_amz_FramedImage_api(h.product_id, h.moulding_id, 
					h.mount.color, h.mount_size, image_width)
			else:
				framed_img = get_amz_FramedImage_api(h.product_id, h.moulding_id, 
					None, h.mount_size, image_width)
				
			f_nm = "f_"
		else:
			framed_img = get_amz_FramedImage_api(h.product_id)
			f_nm = "n_"
			
		env = settings.EXEC_ENV
		img_url = ''
		if env == 'DEV' or env == 'TESTING':
			img_loc = settings.BASE_DIR + '/artevenue/' + settings.STATIC_URL + "montage_amz_data/images/" 
			img_url = img_loc
		else:
			img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL + "montage_amz_data/images/"
			img_url = 'https://www.artevenue.com' + settings.STATIC_URL + "montage_amz_data/images/"
		
		pos = h.url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		lowres_img_name = h.amazon_sku +"_" + h.url[loc:]
		
		# save image
		framed_img.save(img_loc + lowres_img_name)
		
		'''
		## Create thumbnail and save
		framed_img.thumbnail( (75, 75) )
		pos = h.thumbnail_url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		thumb_img_name = f_nm + h.thumbnail_url[loc:]
		framed_img.save(img_loc + thumb_img_name)
		'''
		
		## Save in urls table
		hf = Montage_amz_data.objects.filter(amazon_key = h.amazon_key).update(	
				framed_url = img_url + lowres_img_name)
		
		print("Saved: " + lowres_img_name)

def get_amz_FramedImage_api(prod_id, frame_id=None, mount_color=None, mount_size=None, user_width=None):

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

			img_with_mount = addMount(img_source, mount_color, m_size, m_size, m_size, m_size)
						
			framed_img = applyBorder( request, img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
		else:
			framed_img = applyBorder( request, img_source, moulding['url'], border, border, border, border,
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

def createAmazonFile_campaign():
	
	##ids = [9340,9341,32597,2598,42400,76998,76999,99947,99948,99949,153812,170876,170877,219076,252006,252029,252040,226234,226235,236091,32695,32696,42386,42383,42388,31809,31810,55175,55176,55177,119917,119918,119921,121675,121683,121685,198876,219771,220942,220493,221155,231333,231334,231335,234652,239355,254125,254126,254129]

	## Landscape Campaigns
	#ids = [264794, 246920, 232260, 255409, 220235, 254133, 218493, 247803, 265654, 267538, 243158, 255411, 117791, 204401]

	## Floral Campaigns
	#ids = [235444, 157496, 208355, 210840, 36137, 150212, 207291, 264553, 153125, 153129, 153102, 151536, 175434, 192519, 174947, 235444]

	## Abstract Campaigns
	ids = [119513,193908,87845,47869,36120,238888,255004,195569,240176,78373,80171,262895,263713,218461,280822]

	
	amz = Montage_amz_data.objects.filter(is_published = True, product_id__in = ids,
		amazon_sku__startswith = 'MNCA').order_by('amazon_sku')
		
	with open('Montage_amz_data_advTemplate.csv', 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row =['product_type', 'Seller SKU', 'Brand', 'Product ID', 'Product ID Type',
			'Item Name', 'Manufacturer Part Number', 'Recommended Browse Nodes', 
			'Color Name', 'Color Map', 'Size', 'Included Components', 
			'Enclosure Material', 'Size Map', 'Batteries Included', 'Standard Price',
			'Quantity', 'Maximum Retail Price', 'Main Image URL',
			  
			## Images
			'Other Image URL1', 'Other Image URL2', 'Other Image URL3', 'Other Image URL4',
			'Other Image URL5', 'Other Image URL6', 'Other Image URL7', 'Other Image URL8',
			'Swatch Image URL', 
			
			## Variation
			'Relationship Type', 'Variation Theme', 'Parent SKU', 'Parentage',
			  
			## Basic
			'Update Delete', 'Manufacturer', 'Description', 'Model', 
			
			## Discovery
			'Catelog Number', 'Search Terms', 'Bullet Point1', 'Bullet Point2', 'Bullet Point3',
			'Bullet Point4', 'Bullet Point5', 'Occassion', 'Pattern', 
			'Product Features1', 'Product Features2', 'Product Features3',
			'Product Features4', 'Product Features5', 'Wattage', 'Wattage Unit of Measure',
			'Style', 'Scent', 'Number of Pieces', 'Power Source',
			'Target Audience Base1', 'Target Audience Base2', 'Target Audience Base3',
			'Target Audience Base4', 'Target Audience Base5', 
			'Platinum Keyword1', 'Platinum Keyword2', 'Platinum Keyword3', 'Platinum Keyword4',
			'Platinum Keyword5', 'Platinum Keyword6', 'Platinum Keyword7', 'Platinum Keyword8',
			'Platinum Keyword9', 'Platinum Keyword10', 'Platinum Keyword11', 'Platinum Keyword12',
			'Platinum Keyword13', 'Platinum Keyword14', 'Platinum Keyword15', 'Platinum Keyword16',
			'Platinum Keyword17', 'Platinum Keyword18', 'Platinum Keyword19', 'Platinum Keyword20',
			'length Range', 'Manufacturer Contact', 'Shaft Type', 'Imported By', 
			
			## Diamesions
			'Shipping Weight',
			'Website Shipping Weight Unit of Measure', 'Shape', 'Item Volume', 'Item Volume Unit of Measure',
			'Item Height', 'Item Height Unit of Measure', 'Item length', ' Item Length Unit of Measure',
			'Item Width', 'Item Width Unit of Measure', 'Item Weight', 'Item Weight Unit of Measure',
			'Display Weight', 'Item Display Wight Unit of Measure', 'Display Width', 
			'Item Display Width Unit of Measure', 'Display Depth', 
			'Item Display Depth Unit of Measure', 'Tree Size', 'Volume Capacity Name Unit of Measure',
			'Item Display Diameter', 'Width Range', 'Volume', 'Display Length',  'Display Length Unit of Measure',
			
			##Fulfilment
			'Package Height', 'Package Width', 'Package Length', 'Package Diamensions Unit of Measure',
			'Package Weight', 'Package Weight Unit of Measure', 'Fulfilment Center ID', 
			
			#Compliance
			'Country/Region of Origin',
			'Battary Type/Size 1', 'Battary Type/Size 2', 'Number of Batteries 1',  'Number of Battaries 2', 
			'Number of Batteries 3',
			'Warranty Description', 'Safety Warning', 'Legal Disclaimer',
			
			'Is Product a Battery or Does it Use Batteries', 'Battery Composition', 
			'Battery Weigth', 'Battery Weigth Unit of Measure', 'Number of Lithium Metal Cells',
			'Lithium Battery Packing', 'Watt Hours per Battery', 'Lithium Battery Energy Content Unit of Measure',
			'Lithium Content', 'Lithium Battery Content', 'Lithium Battery Wigth Unit of Measure', 
			'Applicable Dangerous Good Regulations 1', 'Applicable Dangerous Good Regulations 2',
			'Applicable Dangerous Good Regulations 3', 'Applicable Dangerous Good Regulations 4',
			'Applicable Dangerous Good Regulations 5', 'UN Number', 'Safety Datasheet URL', 'Flash Point',
			'HSN Code', 'Categorization / GHS Pictogram 1',  'Categorization / GHS Pictogram 2',
			'Categorization / GHS Pictogram 3', 
				
			## Offer
			'Handling Time', 'Item Condition', 'Offer Condition Note', 'Launch Date', 'Release Date',
			'Number of Items', 'Item Package Quantity', 'Sale Start Date', 'Sale End Date', 
			'Sale Price', 'Restatock Date', 'Is Giftwrap Avaiable?', 'Can Gift be Messaged?',
			'Is Discontinued by Manufacturer', 'Product Tax Code', 'Max Order Quantity', 
			'Stop Selling Date', 'Shipping-Template', 'Offering Release Date',
			
			##B2B
			'Business Price', 'Qualityt Price Type', 'Quantity Price 1', 'Quantity Lower Bound 1',
			'Quantity Price 2', 'Quantity Lower Bound 2', 'Quantity Price 3', 'Quantity Lower Bound 3',
			'Quantity Price 4', 'Quantity Lower Bound 4', 'Quantity Price 5', 'Quantity Lower Bound 5',
			'Pricing Action'
			
			]
		wr.writerow(row)
		for h in amz:
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

			prod_details = "Abtract Painting with frame," + " Title: " + h.product_name + ", Artist: " + h.artist + ".\nPrinted on: " + h.print_medium_id.title() + "; Framed Art Print. "
			prod_details = prod_details + "Image Size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + "; \n"
			incl_components = "One piece abstract art with frame, printed on " + h.print_medium_id.title() + "; "
			incl_components = incl_components + "Image Print Size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + "; "
			if h.moulding_id:
				bullet1 = 'Printed on ' + h.print_medium_id.title() + ', size: ' + str(formatNumber(h.image_width + (h.moulding.width_inner_inches *2) + (h.mount_size *2) )) + " X " + str(formatNumber(h.image_height + (h.moulding.width_inner_inches * 2) + ( h.mount_size * 2) )) + " inch. "
			else:
				bullet1 = "Printed on " + h.print_medium_id.title() + ", size: " + str(formatNumber(h.image_width)) + " X " + str(formatNumber(h.image_height)) + " inch. "
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
			
			t_size = str(formatNumber(t_size_width)) + " X " + str(formatNumber(t_size_height)) + " inch "
			prod_details = prod_details + "Product Size (with frame): " + t_size
			incl_components = incl_components + "Product Size  (with frame): " + t_size
			
			bullet3 = ''
			if h.acrylic_id:
				if h.print_medium_name == "PAPER":
					prod_details = prod_details + "\nThe artwork is covered with clear acrylic for added protection, durability and clear visibility. Acrylic is light weight and durable."
					incl_components = incl_components + "Acrylic covered; "
					bullet3 = "Paper: NovaJet Matte Coated Premium Paper 230 (MCP 230). It is a heavy weight, bright white, smooth finish matte paper, top-coated with an ink-receptive layer. Ideally suitable for printing high quality fine art reproduction. The artwork is covered with clear acrylic for added protection, durability and clear visibility."
				else:
					bullet3 = "Canvas: NovaJet Artistic Matte Canvas 410 (AMC 410). It is a water-resistant canvas, top-coated with an ink-receptive layer. Ideally suitable for fine art reproductions."
			#if i.stretch_id:
			#	prod_details = prod_details +  + "Canvas Stretched; "

			search_terms = ("home decor art painting with frame for living room, bed room wall " + h.key_words.replace('|', ' '))
			
			## Convert to upper case and remove duplicate words, limit to 150 chars
			search_terms = ' '.join(set(search_terms.upper().split()))[:150]
			
			parentSKU = h.parent_amz_sku
			parent_child = h.parent_child
			if parent_child == 'P' or parent_child == '' or parent_child is None:
				parentage = 'Parent'
				variation = ''
				col = ''
				col_map = ''
				p_size = ''
				size_map = ''
				qty = ''
				item_total = 0
				parent_amz_sku = ''
			else:
				parentage = 'Child'
				variation = 'Variation'
				col = 'Multi'
				col_map = 'Multi'
				p_size = 'Size: ' + str(breadth) + '" X ' + str(length) + '" (inches), Printed on ' + h.print_medium_id.title()
				size_map = 'Medium'
				qty = '1000'
				item_total = h.item_total
				parent_amz_sku = h.parent_amz_sku
			
			standard_price = round(item_total + (item_total * 25 / 100),0)
			sale_price = item_total
			
			if h.image_type == '0':
				prod_name = "Arte' Venue: Abstract painting with frame, Title: " + h.product_name + '; Artist: ' + h.artist + '; Framed Art Print (' + t_size + ') '
			else:
				prod_name = "Arte' Venue: Abtract art with frame, Title: " + h.product_name + '; Artist: ' + h.artist + ' - Framed Art Print(' + t_size + ') '

			update_delete = "Update"
			if h.image_width > h.max_width or h.image_height > h.max_height:
				update_delete = "Delete"
			
			
			row =['furnitureanddecor', h.amazon_sku, "Arte' Venue", 
					'', '', prod_name, h.part_number, '4380583031',
					col, col_map, p_size, incl_components, 'Others',
					size_map,'FALSE', standard_price, qty, standard_price, h.framed_url,
					"", "", "", "", "", "", "", "" , "",
					variation, 'Size', parent_amz_sku, parentage, update_delete,
					"Arte'Venue", prod_details + "\n\nArte'Venue strives for high customer satisfaction. You will not be disappointed with the quality of this art print. We have over 2.5 lakh licensed artworks from across the world to choose from. \n\nWe offer customization. Please send us a message with your requirements."[:2000],
					'NA',
					
					##-- Discovery
					'', search_terms, 'This is a licensed artwork. We produce professional quality art print of this painting, frame it and deliver. Your satisfaction is guaranteed.', bullet1, bullet2, bullet3, 'Custom made for you and ready to be hung on the wall', 
					"", "", "", "", "", "", "", "" , "", 'Art Deco', '',
					1, 
					"", "", "", "", "", "", "", "" , "", "",
					"", "", "", "", "", "", "", "" , "", "",
					"", "", "", "", "", "",
					
					"", "(+91) 789 980 4293", "", ""
					
					## - Diamensions
					"", "", "", 'Square/Rectangle',

					"", "", "", "", "", "", "", "" , "", "",
					"", "", "", "", "", "", "", "" , "", "",
					"", "", "", "", "",

					##-- Fulfilment
					"", "", "" , "", "",
					"", "", 
					
					##-- Compliance
					"India", "", "", "", "", "", "",
					'Carries no warranties', 'NA',  
					'Customized product. Return/Refund in case of damaged product delivery. The colors seen and product sizes specificed may change slightly.',
					'FALSE', 
					"", "", "", "", "", "", "", "" , "", "",
					"", "", "", "", "", "", "", "" , "", "",
					"", "", 

					##-- Offer
					'5', "", "", "", "2020-02-26" , "2020-08-31", sale_price, "", "", "", 
					"", "", "", "", "", "", "", "" , "", 

					##-- B2B
					"", "", "", "", "", "", "", "" , "", "",
					"", "", "", "", "", "", "", "" , "", "",
					"", "", "", "", "", "", "", "" , "", "",
					"", "", 
				
				]
				
			wr.writerow(row)

def amazon_data_campaigns():


	##landscape_ids = [264794, 246920, 232260, 255409, 220235, 254133, 218493, 247803, 265654, 267538, 243158, 255411, 117791, 204401]
	#floral_ids = [235444, 157496, 208355, 210840, 36137, 150212, 207291, 264553, 153125, 153129, 153102, 151536, 175434, 192519, 174947, 235444]

	abstract_ids = [119513,193908,87845,47869,36120,238888,255004,195569,240176,78373,80171,262895,263713,218461,280822]


	curated = Stock_image.objects.filter(product_id__in = abstract_ids)
	createAmazonData_campaigns(curated)

def createAmazonData_campaigns(curated):
	
	cnt = 0
	##sku_suf = "AVCL" ## Lanscape
	#sku_suf = "AVCF" ## Floral
	sku_suf = "MNCA" ## ABSTRACT

 	##sku_int = 550000  ## for Kids	
	sku_int = 1001  

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
		
		#####################################################
		# Generate Amazon SKU Number
		#####################################################
		sku_int = sku_int + 1
		parent_sku = sku_suf + str(sku_int)
		#####################################################
		# END: Generate Amazon SKU Number
		#####################################################

		#########################################################
		## Create parent record first - PAPER
		#########################################################
		hl = Montage_amz_data(
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
			quantity = 0,
			item_unit_price = 0,
			item_sub_total = 0,
			item_disc_amt  = 0,
			item_tax  = 0,
			item_total = 0,
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
			image_width = 0,
			image_height = 0,
			created_date = today,
			updated_date = today,
			parent_child = 'P',
			parent_amz_sku = ''
		)
		hl.save()		
		

		
		#########################################################
		## Create 5 versions with different sizes
		#########################################################
		#sizes = [12, 18, 24, 30, 36]
		sizes = [8, 12, 18, 24, 30]

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


			moulding_id = 18 # Simple Black
				
			
			moulding = Moulding.objects.get( moulding_id = moulding_id )
			moulding_name = ''
			if moulding:
				moulding_name = moulding.name

			mount = Mount.objects.get(pk=3)   ## Offwhite
			mount_color = ''
			if mount :
				mount_color = mount.color
		
			if size == 8 or size == 12 or size == 18:
				mount_size = 1
			else:
				mount_size = 2
				
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
			# Generate Amazon SKU Number
			#####################################################
			sku_int = sku_int + 1
			amz_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Amazon SKU Number
			#####################################################
			
			'''
			if size == 12:
				parent_child = "P"
				parent_sku = amz_sku
			else:
				parent_child = "C"
			'''
			
			#####################################################
			# Create Amazon DATA
			#####################################################
			## Insert or Update
			promo_name = ''
			if promotion:
				promo_name = promotion.name
			hl = Montage_amz_data(
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
			amz_sku = sku_suf + str(sku_int)
			#####################################################
			# END: Generate Amazon SKU Number
			#####################################################
			
			'''
			if size == 12:
				parent_child = "P"
				parent_sku = amz_sku
			else:
				parent_child = "C"
			'''
			
			#####################################################
			# Create Amazon DATA - CANVAS
			#####################################################
			## Insert or Update
			promo_name = ''
			if promotion:
				promo_name = promotion.name
			hl = Montage_amz_data(
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
				mount_name = '',
				mount_size = 0,
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

	
	print("Data creation/Update complete: Count - " + str(cnt) )

			
from artevenue.models import Stock_image_category, Product_type, Tax
from artevenue.models import Stock_image, Stock_image_stock_image_category
from artevenue.models import Ecom_site, Publisher_price, Publisher, Curated_collection
from artevenue.models import Stock_image_error, Stock_image_category_error, Product_view
from artevenue.models import Publisher_error, Stock_image_stock_image_category_error, Image_url_error

from artevenue.models import Collage_stock_image, Stock_collage
from gallerywalls.models import Gallery_item, Gallery

from datetime import datetime
from django.conf import settings
from decimal import Decimal
import csv
import urllib
import datetime
import codecs
from pathlib import Path

from PIL import Image, ImageFilter
import requests
from io import BytesIO

from urllib.error import URLError, HTTPError

ecom = Ecom_site.objects.get(store_id=settings.STORE_ID )
today = datetime.date.today()

def importPODImageData(): 

	'''
	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	file = urllib.request.urlopen(url)
	if file.code != 200:
		print ("File not found on POD!")
		return		
	cr = csv.reader(codecs.iterdecode(file, 'utf-8'))	
	
	'''
	##### Down the POD file for processing -
	downloadPODFile()
	cfile = Path('PODFile.csv')
	if not cfile.is_file():
		print("PODFile.csv file did not downloaded")
		return
	file = open('PODFile.csv')	
	cr = csv.reader(file, delimiter=',')
	

	#### Start processing
	cnt = 0
	'''Get Product type (IMAGE) '''
	prod_type = Product_type.objects.filter(product_type_id__iexact = "STOCK-IMAGE", store = ecom).first()
	'''Get Tax code for IMAGE '''
	prod_tax = Tax.objects.filter(name__iexact = "STOCK-IMAGE", store = ecom).first()
	tax_rate = prod_tax.tax_rate

	import wget
	
	img_dir = "/home/artevenue/website/estore/static/image_data/POD/images/"
	
	for row in cr:
		if cnt == 0:	## Skipping first header row
			cnt = cnt + 1
			continue
		cnt = cnt + 1

		print(cnt)

		try:
			row[0]
			row[14]
		except IndexError:
			err_flag = True
			err = Stock_image_error (
				row_id = int(row[0]),
				name = row[4],
				error = 'LIST INDEX ERROR:- '.join(row),
				created_date = datetime.datetime.now(),
				updated_date = datetime.datetime.now()		
			)
			err.save()
			continue

		if row[0]:
			prod = Stock_image.objects.filter(product_id = int(row[0])).first()
			if not prod:

				## Low Resolution Image
				lowres_url = row[11].replace(' ', '%20')
				print("NEW:- " + lowres_url + "\n")
				try:
					fl =  urllib.request.urlopen(lowres_url)
				except HTTPError as e:
					print('Error code: ', e.code)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + lowres_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()					
					continue
				except URLError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + lowres_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
				except ValueError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + lowres_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
					
				if fl.code == 200:
					pos = lowres_url.rfind('/')
					loc = 0
					if pos > 0:
						loc = pos+1
					lowres_img = lowres_url[loc:]
					mfile = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img)
					# If file does not exists then copy the file
					if not mfile.is_file():	
						wget.download(lowres_url.replace('%20', ' '), out=img_dir)
					
				thumbnail_url = row[12].replace(' ', '%20')
				try :
					ft =  urllib.request.urlopen(thumbnail_url)
				except HTTPError as e:
					print('Error code: ', e.code)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + thumbnail_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
				except URLError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + thumbnail_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
				except ValueError as e:
					print('Reason: ', e)
					err = Image_url_error (
						row_id = int(row[0]),
						name = row[4],
						err_desc = 'URL opening error ' + thumbnail_url,
						error = e,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
					continue
					
				if ft.code == 200:
					pos_t = thumbnail_url.rfind('/')
					loc_t = 0
					if pos_t > 0:
						loc_t = pos_t+1
					thumbnail_img = thumbnail_url[loc_t:]
					tfile = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
					# If file does not exists then copy the file
					if not tfile.is_file():	
						wget.download(thumbnail_url.replace('%20', ' '), out=img_dir)
						
			
			'''					'''
			''' Publisher 		'''
			'''					'''
			try:
				publisher = Publisher.objects.filter(publisher_id = row[1]).first()
				if not publisher:
					pub = 	Publisher( 
						publisher_id = row[1],
						publisher_name = row[2],
						publisher_group = 'XXX'
					)
					pub.save()
			except Exception as error:
				err_flag = True
				print (error)
				err = Publisher_error (
					row_id = int(row[0]),
					publisher_id = row[1],
					publisher_name = row[2],
					error = error,
					created_date = datetime.datetime.now(),
					updated_date = datetime.datetime.now()		
				)
				err.save()				
				
			try:
				if publisher:
					published = True
				else:
					published = False
									
				## Get image file urls
				#lowres_url = row[11].replace(' ', '%20')
				lowres_url = row[11]
				pos = lowres_url.rfind('/')
				loc = 0
				if pos > 0:
					loc = pos+1
				url = lowres_url[loc:]
								
				##
				#thumbnail_url = row[12].replace(' ', '%20')
				thumbnail_url = row[12]
				pos = thumbnail_url.rfind('/')
				loc = 0
				if pos > 0:
					loc = pos+1
				thumb_url = thumbnail_url[loc:]
				
				if prod:
					disp_seq = prod.category_disp_priority
				else:
					disp_seq = None
				
				if row[5] == 'Huynh, Duy':
					min_width = 16
					min_height = 16
				else:
					min_width = 10
					min_height = 10
					
				
				## Update Product
				newprod = Stock_image(
					store = ecom,
					product_id = int(row[0]),
					name = row[4],
					description = '',
					price = 0,
					available_on = today,
					updated_at = today,
					part_number = row[3],
					product_type = prod_type,
					is_published = published,
					seo_description = '',
					seo_title  = '',
					charge_taxes = True,
					featured = False,
					has_variants = False,
					aspect_ratio = Decimal(row[6]) / Decimal(row[7]),
					image_type = row[9],
					orientation = row[8].strip().title(),
					max_width = row[6],
					max_height = row[7],
					min_width = min_width,
					publisher = row[1],
					artist = row[5],
					colors = '',
					key_words = row[13],
					url = 'image_data/POD/images/' + url,
					thumbnail_url = 'image_data/POD/images/' + thumb_url,
					category_disp_priority = disp_seq,
					min_height = min_height
				)

				newprod.save()

			except Exception as error:
				err_flag = True
				print (error)
				err = Stock_image_error (
					row_id = int(row[0]),
					name = row[4],
					error = error,
					created_date = datetime.datetime.now(),
					updated_date = datetime.datetime.now()		
				)
				err.save()
			'''					'''
			''' Categories 		'''
			'''					'''
			#get the category id
			category_nm = row[14]
			if row[14] == "Children''s Art":
				category_nm = "Kids"
			
			if row[14] == "":
				category_nm = "Miscellanuous"
				
			prod_category = Stock_image_category.objects.filter(name__iexact = category_nm).order_by('category_id').first()
			if prod_category is None:
				# Insert
				try:
					prod_cat = Stock_image_category(
							store = ecom,
							name = category_nm,
							description = '',
							background_image = '',
							parent = None,
							trending = False,
							url = '',
							featured_collection = False
					)
					prod_cat.save()
					prod_category = prod_cat

				except Exception as error:
					err_flag = True
					print (error)
					err = Stock_image_category_error (
						row_id = int(row[0]),
						category_name = category_nm,
						error = error,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()		
					)
					err.save()
				
			prod_prod_cat = Stock_image_stock_image_category.objects.filter(stock_image_id = row[0]).first()
			
			try:
				if prod_prod_cat :
					prod_cat = Stock_image_stock_image_category(
						id = prod_prod_cat.id,
						stock_image_id = row[0],
						stock_image_category = prod_category
					)
				else :
					prod_cat = Stock_image_stock_image_category(
						stock_image_id = row[0],
						stock_image_category = prod_category
					)
				prod_cat.save()				
				
			except Exception as error:
				err_flag = True
				print (error)
				err = Stock_image_stock_image_category_error (
					row_id = int(row[0]),
					stock_image_category = prod_category,
					error = error,
					created_date = datetime.datetime.now(),
					updated_date = datetime.datetime.now()		
				)
				err.save()
			'''
			publ_price = Publisher_price.objects.filter(publisher_id = row[1], 
				print_medium_id = 'PAPER').first()
				
			if not publ_price:
			
				pub_price = Publisher_price (
					publisher_id = row[1],
					print_medium_id = 'PAPER',
					price_type_id = 'SQIN',
					price = 10.50
				)

				pub_price.save()	

			publ_price = Publisher_price.objects.filter(publisher_id = row[1], 
				print_medium_id = 'CANVAS').first()
			if not publ_price:
			
				pub_price = Publisher_price (
					publisher_id = row[1],
					print_medium_id = 'CANVAS',
					price_type_id = 'SQIN',
					price = 12.50
				)

				pub_price.save()	
			'''
								
	return 
	
	
def deletePODImageData():

	'''
	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	csvfile = urllib.request.urlopen(url)
	if csvfile.code != 200:
		print ("File not found on POD!")
		return
	cr = csv.reader(codecs.iterdecode(csvfile, 'utf-8'))
	'''
	
	##POD file is already downloaded by import program
	cfile = Path('PODFile.csv')
	if not cfile.is_file():
		print("PODFile.csv file did not downloaded")
		return
	file = open('PODFile.csv')	
	cr = csv.reader(file, delimiter=',')
	
	cnt = 0
	d_cnt = 0
	c_cnt = 0
	prod_ids = []
	for row in cr:	
		# Skip the first row (header)
		if cnt == 0:
			cnt = cnt + 1
			continue	
		prod_ids.append(row[0])
	
	if len(prod_ids) == 0:
		print ("No rows in POD file!")
		return

	if len(prod_ids) < 240000 :
		print ("POD File contains less than 2.4 lakh rows, skipping deletion of data.")
		return

	# Get all products
	prods = Stock_image.objects.filter(is_published=True)

	# Get all Sets
	collages = Collage_stock_image.objects.filter(stock_collage__is_published=True)
	
	# Get all Gallery Walls
	gallery_items = Gallery_item.objects.filter(gallery__is_published=True)
	
	for prod in prods:
		if str(prod.product_id) in prod_ids:
			## Check if price is available,if no group is assigned then don't
			## publish the image
			p = Publisher.objects.filter(publisher_id = prod.publisher, publisher_group = 'XXX')
			if p:
				prd = Stock_image.objects.filter(product_id = prod.product_id).update(
						is_published = False)				
						
		else:
			# Set product is_published to false
			if prod.product_id <= 1000000:
				prd = Stock_image.objects.filter(product_id = prod.product_id).update(
						is_published = False)
				d_cnt = d_cnt+1
				print(d_cnt)

		cnt = cnt + 1
		if cnt >= 1000000:
			break	

	##	Remove from collage sets and gallery walls too
	for c in collages:
		cpr = Product_view.objects.filter(product_id = c.stock_image_id,
			is_published = False).first()		
		if cpr:
			stk_collage = Stock_collage.objects.filter( 
			product_id = c.stock_collage ).update( is_published = False)
			d_cnt = d_cnt+11
			
	for g in gallery_items:
		gpr = Product_view.objects.filter(product_id = g.product_id, product_type_id = g.product_type_id,
			is_published = False).first()		
		if gpr:
			gal = Gallery.objects.filter( 
			gallery_id = g.gallery_id ).update( is_published = False)
			d_cnt = d_cnt+1

	print("Total deleted: " + str(d_cnt) )
	print("Total curated deleted: " + str(c_cnt) )
	return cnt
	
def downloadPODFile():
	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	csvfile = urllib.request.urlopen(url)
	if csvfile.code != 200:
		print ("File not found on POD!")
		return

	html = csvfile.read()

	with open('PODFile.csv', 'wb') as f:
			f.write(html)

def getPODImages():
	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	file = urllib.request.urlopen(url)
	if file.code != 200:
		print ("File not found on POD!")
		return
	
	cr = csv.reader(codecs.iterdecode(file, 'utf-8'))		
	#cr = csv.reader(csvfile, delimiter=',')

	cnt = 0
	for row in cr:
		# Skip the first row (header)
		cnt = cnt + 1
		if cnt == 0:
			continue

		if cnt < 10000:
			continue
			
		## Low Resolution Image
		lowres_url = row[11]
		pos = lowres_url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		lowres_img = lowres_url[loc:]
		file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img)
		# If file does not exists then copy the file
		if not file.is_file():	
			res = requests.get(lowres_url)
			img = Image.open(BytesIO(res.content))
			img.save("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img, 'JPEG')
		
		thumbnail_url = row[12]
		pos = thumbnail_url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		thumbnail_img = thumbnail_url[loc:]
		file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
		# If file does not exists then copy the file
		if not file.is_file():	
			res = requests.get(thumbnail_url)
			img = Image.open(BytesIO(res.content))
			img.save("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img, 'JPEG')

		if cnt%100 == 0:
			print( str(cnt/100) + ' images done...')
		
		if cnt >= 20000:
			break
		

def getPODImagesWget():
	import wget

	url = "https://www.podexchange.com/pod-export/fc30cfbd-50ba-4d40-b29f-cdc10dd88f66.csv"
	file = urllib.request.urlopen(url)
	if file.code != 200:
		print ("File not found on POD!")
		return
	
	cr = csv.reader(codecs.iterdecode(file, 'utf-8'))		
	#cr = csv.reader(csvfile, delimiter=',')

	cnt = 0
	img_dir = "/home/artevenue/website/estore/static/image_data/POD/images/"
	for row in cr:
		# Skip the first row (header)
		
		if cnt == 0:
			cnt = cnt + 1
			continue
		cnt = cnt + 1
		
			
		## Low Resolution Image
		lowres_url = row[11].replace(' ', '%20')
		print('ROW: ' + row[0])
		print(lowres_url)
		fl =  urllib.request.urlopen(lowres_url)
		if fl.code == 200:
			pos = lowres_url.rfind('/')
			loc = 0
			if pos > 0:
				loc = pos+1
			lowres_img = lowres_url[loc:]
			file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img)
			# If file does not exists then copy the file
			if not file.is_file():	
				print(lowres_url)
				wget.download(lowres_url.replace('%20', ' '), out=img_dir)
				
				#res = requests.get(lowres_url)
				#img = Image.open(BytesIO(res.content))
				#img.save("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img, 'JPEG')
			
		thumbnail_url = row[12].replace(' ', '%20')
		ft =  urllib.request.urlopen(thumbnail_url)
		if ft.code == 200:
			pos_t = thumbnail_url.rfind('/')
			loc_t = 0
			if pos_t > 0:
				loc_t = pos_t+1
			thumbnail_img = thumbnail_url[loc_t:]
			file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
			# If file does not exists then copy the file
			if not file.is_file():	
				print(thumbnail_url)
				wget.download(thumbnail_url.replace('%20', ' '), out=img_dir)

		if cnt%100 == 0:
			print( str(cnt/100) + ' images done...')
		
		if cnt >= 100000:
			break
		

def category_priority():

	ids = [47851, 47852, 218528, 311997, 280889, 42748, 148968, 148970, 218461, 218467, 42765, 218524, 311989, 43278, 43279, 43280, 65039, 280972, 312015, 312017, 43304, 43305, 167408, 218458, 244131, 47876, 244135, 244136, 149071, 167409, 47870, 144355, 144356, 144357, 101918, 124306, 12037, 12038, 36708, 36709, 171275, 171276, 171277, 176064, 142713, 137527, 80073, 80074, 78374, 78375, 80167, 80168, 172405, 172406, 172407, 172408, 119513, 176170, 199441, 201556, 193907, 193908, 154549, 154550, 78932, 78933, 137784, 137785, 137786, 32636, 23675, 23676, 158969, 158970, 19381, 19382, 31687, 87838, 87840, 87848, 87851, 183349, 183350, 183445, 47869, 158384, 59347, 59348, 59359, 59360, 59363, 59364, 59365, 59366, 59367, 59384, 59385, 166669, 274322, 274323, 19147, 158933, 158934, 33465, 21167, 19191, 123535, 123536, 33886, 33887, 17110, 10146, 53468, 53469, 206552, 310156, 310174, 36120, 36121, 36205, 36207, 36208, 36209, 36213, 36224, 36365, 36399, 41152, 210846, 210847, 232195, 192869, 192868, 193058, 193059, 192612, 264782, 270652, 208924, 227960, 227959, 322544, 237784, 237785, 238888, 150326, 231156, 231157, 231158, 148083, 148084, 148085, 255004, 174621, 174622, 174623, 174624, 174619, 174620, 183445, 183533, 183534, 196693, 195567, 195568, 195569, 195570, 209236, 263709, 199495, 199496, 214775, 214776, 215028, 215029, 215030, 215138, 215139, 267776, 267778, 267779, 229852, 229853, 230501, 244682, 244683, 245069, 245070, 258740, 258741, 258742, 274478, 274479, 270934, 270935, 140371, 140372, 98879, 301251, 302341, 302342, 302343, 302344, 302345, 302346, 313071, 313072, 313124, 313125, 313695, 313696, 327532, 327533, 327534, 327591, 327592, 327601, 327609, 327713, 327714, 328057, 328058, 170030, 282760, 282762, 87929, 87939, 87940, 184419, 31660, 31688, 31689, 240243, 315467, 315476, 278296, 278298, 150149, 150150, 240149, 281265, 220159, 240174, 240176, 240177, 240179, 261359, 322826, 322827, 332669, 332717, 82645, 82646, 234180, 234250, 261477, 321867, 321870, 151296, 151288, 151292, 225282, 215696, 215697, 215698, 251730, 225303, 310986, 310990, 310993, 310994, 310992, 310996, 199272, 184488, 211197, 211198, 108079, 117663, 99621, 315153, 319764, 241498, 241534, 241562, 241563, 241598, 193771, 320276, 325198, 322013, 322012, 321180, 321186, 87837, 87841, 87844, 87845, 204559, 263161, 263162, 142709, 142710, 307495, 79543, 13428, 13429, 79573, 79574, 142713, 80075, 80139, 137572, 80158, 193424, 78372, 78373, 270629, 80171, 80172, 262895, 262896, 119471, 119472, 251738, 251739, 226400, 217397, 263713, 263714, 251740, 226118, 226119, 255464, 232351, 232352, 232368, 232369, 232372, 232373, 232381, 232383, 232385, 232386, 232390, 304294, 298986, 298987, 283005, 283006, 304337, 304338, 307952, 170988, 171312, 198778, 198786, 194802, 198840, 227301, 227298, 227300, 227299, 280826, 280827, 280828, 286182, 286183, 286283, 286284, 80247, 158421, 280822, 78895, 30473, 30476, 30477, 156320, 156321, 220311, 220314, 220316, 232465, 156327, 156328, 316929, 193779, 193780, 314936, 316976, 307510, 307534, 74778, 218792, 208338, 321263, 170384, 167257, 167258, 193453, 193454, 193597, 193598, 280896, 280897, 193492, 193456, 117960, 117961, 330269, 30399, 78747, 79513, 79089, 23865, 47255, 87899, 254786, 254787, 166523, 166522, 167541, 167542, 167543, 310564, 310565, 207275, 207276, 207277, 207278, 207287, 207291, 74008, 47359, 74009, 74010, 204705, 204706, 31764, 205771, 21261, 205773, 11750, 19080, 7935, 21989, 21417, 309803, 226074, 226075, 201563, 201564, 202075, 202076, 36090, 36091, 36137, 36237, 36276, 36277, 36383, 41127, 95652, 57564, 151215, 57568, 57569, 55766, 55767, 36458, 164592, 170949, 170950, 194798, 198642, 190045, 73354, 190079, 193815, 193816, 208354, 208360, 210760, 210761, 208364, 208365, 217435, 208422, 208509, 208510, 210797, 208543, 210840, 258166, 258167, 192956, 192957, 153129, 153127, 153126, 153125, 153128, 153123, 153122, 153121, 153111, 153110, 153102, 153087, 283879, 283877, 283878, 157761, 157697, 157658, 157696, 157659, 158831, 157719, 163677, 170772, 170771, 170770, 192835, 192822, 192823, 192794, 171963, 174517, 228041, 228040, 227593, 227592, 175434, 219906, 219905, 219907, 192615, 211628, 211661, 211665, 195103, 235444, 201762, 201763, 221428, 219064, 217500, 219732, 221576, 221595, 221596, 298527, 246608, 246618, 246619, 246662, 246663, 246698, 246699, 298537, 264576, 264577, 264122, 264714, 264718, 264791, 208753, 208754, 208777, 208780, 270676, 276207, 227342, 227343, 227341, 298629, 298732, 298733, 298735, 298736, 298783, 211420, 310867, 212982, 219868, 247334, 239806, 231449, 231451, 247347, 247454, 247859, 247860, 204126, 204127, 258068, 258069, 329510, 329512, 322408, 308628, 308629, 308630, 198716, 198717, 237464, 237465, 237468, 237469, 248686, 248687, 270388, 270389, 61056, 155286, 155287, 155288, 246315, 246316, 209287, 209288, 214787, 217272, 217273, 217274, 217961, 234350, 259578, 252771, 252772, 165846, 165847, 311390, 251712, 251713, 251714, 170086, 170087, 310929, 310930, 310931, 213254, 194050, 194051, 240659, 240660, 240663, 262466, 262467, 315771, 315772, 154539, 316032, 190587, 190588, 219923, 240147, 176096, 240186, 240187, 240196, 240197, 332654, 332655, 234281, 283097, 283098, 59925, 73112, 213350, 213352, 213362, 213363, 36721, 36722, 197440, 250467, 149633, 176107, 220175, 199419, 199420, 220181, 220186, 220187, 220188, 220190, 220191, 220192, 232319, 232320, 232321, 232323, 232324, 232325, 232327, 232328, 232335, 232336, 232337, 240206, 240207, 261391, 261392, 261399, 261400, 261409, 261221, 261225, 261234, 261235, 261236, 261239, 261242, 261243, 261249, 261250, 281401, 78705, 78706, 281431, 330774, 193905, 193906, 176013, 173771, 260753, 29009, 29010, 36814, 165879, 165878, 316600, 316601, 307632, 263256, 158425, 169933, 169934, 232402, 158291, 158298, 158299, 158300, 171015, 171016, 171065, 171066, 204231, 204232, 176143, 176144, 176145, 220226, 220232, 220371, 220258, 240212, 240213, 240214, 281444, 332778, 332779, 316815, 232463, 202113, 202114, 202115, 202116, 154669, 154670, 226157, 316840, 316841, 316845, 316846, 219647, 262750, 262751, 87896, 87897, 193910, 162620, 162621, 87332, 87333, 87334, 214517, 261316, 261317, 37030, 310051, 35917, 55558, 32574, 310141, 36092, 162988, 36382, 198601, 198602, 95758, 95759, 151051, 36428, 93492, 201980, 194321, 208386, 208387, 208388, 208390, 246488, 210776, 208521, 210808, 210809, 208600, 208601, 324134, 105926, 149212, 137634, 137644, 137655, 137643, 94103, 211685, 211684, 219058, 217481, 221557, 246530, 246531, 246546, 246547, 276094, 264623, 264624, 264630, 264631, 264642, 264643, 264693, 239681, 270646, 270647, 270649, 270650, 276187, 298690, 298691, 298692, 211598, 220470, 220471, 298744, 257714, 257715, 257716, 257717, 211405, 325542, 325543, 307363, 211357, 325557, 326834, 211504, 326838, 322372, 283790, 252360, 247062, 247102, 304668, 204118, 204119, 204123, 204150, 204152, 204153, 204154, 204155, 262003, 262004, 262027, 262028, 262031, 262032, 322432, 322506, 311957, 311958, 326322, 326323, 326324, 322725, 326341, 329797, 329810, 198686, 198687, 198688, 204171, 204172, 204173, 204189, 204190, 204191, 204195, 204196, 204197, 204199, 204200, 312345, 312346, 312347, 202080, 202081, 202082, 105916, 154897, 154898, 154899, 154903, 154904, 154905, 164720, 204331, 204332, 196465, 196466, 196516, 196517, 209745, 209746, 204376, 274378, 274379, 228394, 228396, 228397, 228398, 229771, 229968, 229969, 258224, 258225, 258304, 258305, 258306, 258360, 258361, 301138, 302550, 302552, 302554, 302562, 302563, 302564, 302701, 302702, 312644, 312645, 312823, 312824, 313163, 313164, 313454, 313455, 314123, 314124, 329368, 329369, 329370, 329371, 328355, 328356, 328838, 328839, 328840, 328841, 328859, 328860, 328873, 328874, 328961, 328962, 95231, 243058, 103623, 208323, 202800, 202801, 278242, 278243, 278247, 278244, 278246, 333047, 333063, 320961, 320966, 330406, 330407, 330408, 330409, 150927, 150928, 150931, 150932, 307297, 194015, 194016, 240273, 240274, 275985, 318112, 318113, 318114, 333123, 333124, 333125, 242819, 242822, 198944, 254847, 243068, 243063, 332631, 332658, 327008, 332659, 332660, 332661, 332670, 332671, 332672, 332673, 282303, 246707, 282360, 282361, 246820, 246821, 246721, 279024, 279025, 279027, 279028, 280791, 199035, 215782, 322003, 316389, 316390, 118358, 118361, 118362, 303023, 243197, 211194, 243978, 243980, 330884, 245984, 245985, 245986, 246002, 246004, 282207, 275894, 172600, 172601, 225317, 225320, 225321, 307200, 334094, 334107, 334108, 334109, 319046, 319056, 319067, 319068, 319072, 319738, 319739, 319751, 319752, 319753, 319754, 277186, 211024, 211027, 262710, 262355, 262720, 271001, 278942, 271002, 278943, 271003, 283529, 283531, 224241, 224242, 224243, 251247, 257334, 257335, 199237, 199238, 199239, 199240, 282879, 307642, 140083, 140084, 140088, 140089, 140090, 170193, 170195, 170194, 243999, 244003, 244004, 244006, 324123, 198798, 286205, 286206, 286207, 286208, 286279, 220222, 220223, 220224, 220230, 220234, 220253, 220254, 220255, 334613, 202137, 322042, 325637, 325638, 314678, 314684, 314688, 314701, 318424, 318425, 318429, 322052, 210758, 320004, 320005, 320006, 208125, 208128, 320825, 320827, 320831, 174176, 167106, 167107, 334683, 334684, 334685, 334687, 334688, 334689, 303759, 303760, 303761, 303762, 303764, 303765, 303766, 208209, 208210, 191862, 280625, 280626, 307519, 307706, 171399, 171401, 107764, 220325, 220326, 208339, 161232, 161237, 280775, 139734, 139736, 139738, 332425, 330106, 330033, 244170, 244171, 218385, 270249, 281081, 330005, 330027, 330122, 330064, 244169, 244172, 118236, 118237, 207048, 207049, 310409, 124069, 124070, 124071, 124072, 124073, 310557, 205384, 205388, 205489, 205490, 28341, 206553, 309472, 197538, 197537, 197536, 197535, 197534, 197529, 171871, 78096, 78095, 78065, 78064, 78063, 78062, 254939, 244016, 83324, 83323, 146039, 146038, 64169, 145750, 145473, 63760, 63759, 199440, 72730, 72729, 204212, 198836, 160750, 150794, 150793, 150787, 73323, 73322, 145107, 145106, 307683, 307682, 307489, 307488, 307487, 307648, 310623, 310622, 190513, 325232, 325176, 325174, 317664, 317663, 213511, 213505, 250009, 144925, 63696, 63695, 260697, 260699, 260894, 144813, 144812, 144811, 144810, 160660, 160659, 317825, 317824, 160613, 160612, 160611, 160609, 160607, 160606, 160605, 241245, 223720, 223719, 200341, 200340, 330769, 330767, 330702, 250617, 79121, 79120, 142550, 142549, 59433, 59427, 94017, 94016, 260255, 259809, 259808, 167031, 167030, 197440, 140017, 219271, 219268, 219266, 65910, 198767, 170431, 332557, 282816, 202302, 333378, 317202, 317189, 317188, 317186, 317157, 317156, 164402, 164401, 164400, 164399, 119211, 119210, 119201, 286081, 255031, 255029, 240571, 143517, 143516, 162995, 162994, 212075, 212073, 212072, 65936, 65937, 328891, 328794, 328793, 121623, 121622, 183876, 183875, 165845, 165844, 259774, 259773, 259772, 259771, 259770, 259406, 259405, 258791, 258790, 258769, 258768, 215216, 215215, 215214, 215213, 210390, 210389, 210388, 210387, 204653, 204652, 204651, 204650, 197119, 197118, 197117, 197116, 197075, 197074, 196348, 196345, 196095, 196094, 196087, 196086, 182790, 182789, 148109, 148108, 148079, 147992, 147991, 147968, 147967, 147922, 147921, 120669, 120668, 184297, 184296, 38616, 38615, 302764, 302763, 239065, 239064, 238622, 238621, 238619, 238618, 238398, 238397, 238388, 238387, 237597, 312344, 312343, 312342, 326451, 322718, 322702, 322701, 329615, 329614, 329613, 308838, 304727, 304585, 329517, 329516, 304762, 304756, 304757, 304760, 304761, 304758, 286521, 286432, 286431, 278103, 286397, 286396, 308376, 308372, 308371, 298404, 265105, 265106, 204124, 329490, 239830, 239829, 246452, 211424, 211426, 211425, 211427, 211594, 211595, 211596, 298626, 276125, 276124, 246666, 235496, 235495, 235494, 235493, 195063, 211702, 211703, 171874, 137600, 137599, 153072, 304481, 304482, 153093, 93281, 211733, 211732, 73549, 73548, 93262, 93255, 73727, 73630, 304858, 93232, 71981, 150269, 150268, 150267, 150266, 150243, 150242, 150241, 150240, 94082, 170917, 150228, 150222, 150221, 95710, 95666, 59835, 59834, 36253, 36252, 55417, 34276, 207017, 207015, 35877, 206869, 206868, 206850, 206846, 28316, 21374, 206436, 20901, 205863, 205862, 10270, 10269, 159964, 159505, 159504, 17216, 10068, 10067, 47643, 122701, 122700, 122626, 122164, 122087, 122086, 124128, 51372, 51374, 159064, 159063, 124068, 124067, 124066, 124065, 51366, 18091, 18090, 34025, 34024, 124050, 124049, 51389, 51391, 51388, 51385, 51343, 11084, 51349, 51350, 51351, 306921, 121927, 121926, 166424, 87281, 87280, 218443, 193439, 195797, 195796, 307707, 260243, 78572, 160969, 152797, 152796, 312251, 312250, 314693, 226175, 226121, 197541, 211411, 211410, 235978, 235979, 203972, 203975, 150390, 150391, 203976, 203977, 203978, 203979, 236009, 236010, 236012, 236013, 236014, 236034, 236035, 203984, 236071, 236072, 236073, 236075, 236076, 198876, 198877, 198878, 198879, 203988, 203989, 203990, 121673, 121674, 121675, 121676, 121677, 121678, 121679, 121680, 121681, 121682, 121683, 121684, 252509, 311513, 311542, 304607, 304729, 237584, 102005, 102006, 102007, 102008, 102009, 61675, 61676, 60994, 164843, 164853, 164854, 164856, 164857, 164858, 214700, 214701, 228928, 228929, 228978, 228979, 228980, 228984, 228985, 230253, 230254, 230255, 76998, 76999, 313818, 313883, 313884, 313886, 313887, 313888, 313889, 328928, 328929, 242956, 202808, 202809, 32695, 32697, 32698, 32699, 225247, 310949, 333029, 211874, 212112, 307317, 202862, 202863, 9340, 9341, 143707, 143710, 143781, 144134, 144135, 144146, 164125, 219128, 219129, 219134, 219135, 219136, 219137, 219153, 219154, 282440, 282443, 243549, 243550, 243548, 298849, 298852, 222638, 88275, 88279, 88282, 219223, 219226, 213354, 12249, 12250, 19697, 19698, 118340, 199956, 203232, 203233, 333660, 333662, 104877, 104878, 153565, 153570, 232967, 253307, 253308, 253311, 333682, 333683, 333784, 161767, 161768, 161769, 223309, 223310, 223311, 223312, 223313, 223314, 223317, 223318, 200464, 200465, 200466, 200467, 220936, 220937, 333889, 333890, 333891, 333892, 333912, 333922, 333923, 333924, 333925, 333926, 333927, 240460, 240461, 240464, 240465, 246218, 246219, 246220, 246221, 248816, 221156, 221157, 221158, 85387, 277182, 331959, 224182, 224183, 224412, 224419, 224420, 168421, 203650, 213424, 213425, 251455, 254118, 254120, 254124, 254125, 316827, 227431, 227430, 316835, 316836, 316837, 316838, 70774, 70775, 70776, 221669, 221671, 221672, 221678, 221679, 99947, 99948, 99949, 99951, 99998, 99999, 100000, 126352, 126353, 126354, 126355, 126356, 33350, 33351, 33353, 11014, 11015, 281068, 281070, 281071, 281072, 281076, 281077, 281078, 321305, 11291, 321320, 33610, 33611, 33612, 21188, 265492, 265490, 265491, 163642, 163641, 163640, 235280, 195181, 195180, 194992, 194991, 235486, 235487, 235488, 208738, 208739, 208740, 208741, 219076, 235676, 235679, 235680, 235681, 235682, 235683, 310827, 212916, 211413]
	
	for i in ids:
		try:
			prod = Stock_image.objects.get(pk = i)
		except Stock_image.DoesNotExist:
			continue
		if prod:
			if prod.category_disp_priority is None:
				prod = Stock_image.objects.filter(pk = i).update(
					category_disp_priority = 1 )
				print("Updated..." + str(i))
	
	
def getMissingImages():

	##### Down the POD file for processing -
	downloadPODFile()
	cfile = Path('PODFile.csv')
	if not cfile.is_file():
		print("PODFile.csv file did not downloaded")
		return
	file = open('PODFile.csv')	
	cr = csv.reader(file, delimiter=',')
	

	#### Start processing
	cnt = 0
	import wget	
	img_dir = "/home/artevenue/website/estore/static/image_data/POD/images/"
	
	for row in cr:
		if cnt == 0:	## Skipping first header row
			cnt = cnt + 1
			continue
		cnt = cnt + 1

		print(cnt)

		try:
			row[0]
			row[14]
		except IndexError:
			err_flag = True
			err = Stock_image_error (
				row_id = int(row[0]),
				name = row[4],
				error = 'LIST INDEX ERROR:- '.join(row),
				created_date = datetime.datetime.now(),
				updated_date = datetime.datetime.now()		
			)
			err.save()
			continue

		if row[0]:
			## Low Resolution Image
			lowres_url = row[11].replace(' ', '%20')
			
			#fl =  urllib.request.urlopen(lowres_url)
			#if fl.code == 200:
			pos = lowres_url.rfind('/')
			loc = 0
			if pos > 0:
				loc = pos+1
			lowres_img = lowres_url[loc:]
			mfile = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img)

			# If file does not exists then copy the file
			if not mfile.is_file():	
				print("Downloading:- " + lowres_url + "\n")
				try:
					wget.download(lowres_url.replace('%20', ' '), out=img_dir)
				except Exception as e:
					print('Error code: ', e.code)
					continue
					
				
			thumbnail_url = row[12].replace(' ', '%20')
			#ft =  urllib.request.urlopen(thumbnail_url)
			#if ft.code == 200:
			pos_t = thumbnail_url.rfind('/')
			loc_t = 0
			if pos_t > 0:
				loc_t = pos_t+1
			thumbnail_img = thumbnail_url[loc_t:]
			tfile = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
			# If file does not exists then copy the file
			if not tfile.is_file():	
				print("Downloading:- " + thumbnail_url + "\n")
				try:
					wget.download(thumbnail_url.replace('%20', ' '), out=img_dir)
				except Exception as e:
					print('Error code: ', e.code)
					continue

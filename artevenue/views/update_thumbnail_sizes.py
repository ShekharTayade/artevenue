def update_thumbnails(do_upto):

	import wget	
	from PIL import Image
	from django.conf import settings
	from pathlib import Path
	from artevenue.models import Stock_image
	import csv

	img_dir = "/home/artevenue/website/estore/static/image_data/POD/images/"

	done_upto_file = Path('/home/artevenue/website/estore/static/done_upto_file.csv')
	done_upto = 0
	if done_upto_file.is_file():
		file = open('/home/artevenue/website/estore/static/done_upto_file.csv')	
		cr = csv.reader(file, delimiter=',')
		for row in cr:
			done_upto = row[0]

	prods = Stock_image.objects.filter(is_published = True).order_by('product_id')
	if do_upto > 0:
		prods = prods.filter(product_id__lte = do_upto, product_id__gt = done_upto)
	
	for p in prods:		
		prod_id = p.product_id
		print("Processing: " + str(prod_id))
		thumb_url = settings.PROJECT_DIR + "/" + settings.STATIC_URL + p.thumbnail_url
		print("THUMB URL: " + thumb_url)
		if thumb_url:
			t_img = Image.open(thumb_url)
			if t_img:
				if t_img.width <= 300:
					url = settings.PROJECT_DIR + "/" + settings.STATIC_URL + p.url
					print("URL: " + url)
					img = Image.open(url)
					if img:
						ratio = img.width / img.height
						h = round(300 / ratio)
						img_thumb = img.resize((300, h))						
						img_thumb.save(settings.PROJECT_DIR + "/" + settings.STATIC_URL + p.thumbnail_url)
		

	if prod_id:
		with open(done_upto_file, 'w', newline='') as upto_file:
			wr = csv.writer(upto_file, quoting=csv.QUOTE_ALL)
			row =[prod_id]
			wr.writerow(row)
	

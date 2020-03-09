from artevenue.models import Stock_image_category, Product_type, Tax
from artevenue.models import Stock_image, Stock_image_stock_image_category
from artevenue.models import Ecom_site, Publisher_price, Publisher
from artevenue.models import Stock_image_error, Stock_image_category_error, Publisher_error, Stock_image_stock_image_category_error

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


ecom = Ecom_site.objects.get(store_id=settings.STORE_ID )
today = datetime.date.today()

def get70_71k():
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
		cnt = cnt + 1
		if cnt == 0:
			continue

		if cnt < 70000:
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
			wget.download(lowres_url, out=img_dir)
			
			#res = requests.get(lowres_url)
			#img = Image.open(BytesIO(res.content))
			#img.save("/home/artevenue/website/estore/static/image_data/POD/images/" + lowres_img, 'JPEG')
		
		thumbnail_url = row[12]
		pos = thumbnail_url.rfind('/')
		loc = 0
		if pos > 0:
			loc = pos+1
		thumbnail_img = thumbnail_url[loc:]
		file = Path("/home/artevenue/website/estore/static/image_data/POD/images/" + thumbnail_img)
		# If file does not exists then copy the file
		if not file.is_file():	
			wget.download(thumbnail_url, out=img_dir)

		if cnt%100 == 0:
			print( str(cnt/100) + ' images done...')
		
		if cnt >= 71000:
			break
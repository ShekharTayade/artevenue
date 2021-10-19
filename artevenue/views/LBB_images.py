import csv
import urllib
from pathlib import Path
import urllib.request

from PIL import Image


def get_lbb_images():
	cfile = Path('image_urls.csv')
	
	if not cfile.is_file():
		print("image_urls.csv file did not downloaded")
		return
	file = open('image_urls.csv')	
	cr = csv.reader(file, delimiter=',')

	cnt = 0
	for row in cr:
		if cnt == 0:	## Skipping first header row
			cnt = cnt + 1
			continue
		cnt = cnt + 1

		print(cnt)

		try:
			row[0]
		except IndexError:
			err_flag = True
			continue		
		
		if row[0]:
			i_main = i_1 = i_2 = i_3 = i_4 = i_5 = i_6 = i_7 = i_8 = ''
			if row[1]:
				i_main = row[1]
				urllib.request.urlretrieve(row[1], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'.jpg')
			if row[2]:
				i_1 = row[2]
				urllib.request.urlretrieve(row[2], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_1.jpg')
				
			if row[3]:
				i_2 = row[3]
				urllib.request.urlretrieve(row[3], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_2.jpg')
			if row[4]:
				i_3 = row[4]
				urllib.request.urlretrieve(row[4], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_3.jpg')
			if row[5]:
				i_4 = row[5]
				urllib.request.urlretrieve(row[5], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_4.jpg')
			if row[6]:
				i_5 = row[6]
				urllib.request.urlretrieve(row[6], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_5.jpg')
			if row[7]:
				i_6 = row[7]
				urllib.request.urlretrieve(row[7], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_6.jpg')
			if row[8]:
				i_7 = row[8]
				urllib.request.urlretrieve(row[8], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_7.jpg')
			if row[9]:
				i_8 = row[9]
				urllib.request.urlretrieve(row[9], row[0]+".jpg")
				img = Image.open(row[0]+".jpg")
				img.save('C:/artevenue/LBB/feed/images/' + row[0]+'_8.jpg')
			

			
			
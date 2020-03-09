from artevenue.models import Stock_image, Moulding_image, User_image
from django.contrib.auth.models import User
from django.conf import settings

from django.http import HttpResponse
from decimal import Decimal

from PIL import Image, ImageFilter

import requests
from io import BytesIO

import base64
from io import StringIO
from PIL import ExifTags

## Frame.applyFrame(' http://www.podexchange.com/dsi/lowres/52/52_011FIS1332_lowres.jpg ', 'moulding/ornate_cocoa_apply.jpeg', 551, 16, 16)

def applyFrame(img_source, frame_img, slice, user_width, user_height):

	#if prod_img.publisher == '1001':
	#	img_source = Image.open('artevenue/'+settings.STATIC_URL + prod_img.url)			
	#else :
	response = requests.get(img_source.strip())
	user_img = Image.open(BytesIO(response.content))

	# Get the image from the server to extract the frame border
	from django.conf import settings
	path = settings.MOULDING_ROOT + frame_img	
	
	frame_img = Image.open(path)
	#frame_edge = Image.open(path)
	frame_edge = frame_img.crop( (slice, 0, slice + int((frame_img.width-slice) *20/100), slice ) )
	#print(frame_edge.info)
	dpi = 0

	inf = frame_edge.info
	
	if 'dpi' in inf:
		dpi = inf['dpi'][0]

	
	width = int(user_img.width)
	height = int(user_img.height)
	
	framepixels = int(user_img.width / user_width)
	
	framed_size = (int(width + framepixels * 2), int(height + framepixels * 2))

	# Resize the edge to size of the border required
	percent20 = int(frame_edge.width * 20 /100)
	edge = frame_edge.resize( (int(frame_edge.width - percent20), framepixels) )
	for l in range( frame_edge.width - percent20, 20, -percent20):
		edge = edge.resize((l, framepixels))

	# Resize the corner to size of the border required
	#path = settings.MOULDING_ROOT + frame_corner
	#c = Image.open(path)	
	corner = frame_img.crop( (0,0, slice, slice) )

	new_img = Image.new("RGB", (framed_size), 0)

	# Paste user image first
	new_img.paste(user_img, (framepixels,framepixels))	

	new_img.paste(corner, (0,0))
	new_img.paste(edge, (framepixels,0))
	#new_img.show()
	
	
	'''***************
	Repeat border for the TOP EDGE
	'''
	width_to_fill = int(new_img.width - (framepixels + framepixels))  # corners are already placed
	num_of_imgs = width_to_fill // edge.width # number of images that will fit in the edge
	remainder = width_to_fill % edge.width # the remainder part

	curr_coord = int(framepixels)
	for l in range( curr_coord, width_to_fill, edge.width):
		new_img.paste(edge, (l, 0))

	# paste remainder, if any
	if remainder > 0:
		top_rem = edge.crop( (edge.width - remainder, 0, user_img.width, user_img.height) )
		new_img.paste( top_rem, ((width_to_fill + framepixels - remainder), 0))	

	# Resize the corner to size of the border required
	path = settings.MOULDING_ROOT + "/moulding/ornate_cocoa_corner_rt.jpg"
	c = Image.open(path)	
	top_right_corner = c.resize((framepixels, framepixels))	
	
	## Rotate the corner 270 degrees and paste
	#top_right_corner = corner.rotate(270)
	new_img.paste(top_right_corner, (new_img.width - framepixels, 0))
	
	new_img.show()	
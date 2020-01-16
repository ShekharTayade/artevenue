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

## Frame.applyFrame(' http://www.podexchange.com/dsi/lowres/52/52_011FIS1332_lowres.jpg ', 'moulding/classic_touch_apply.jpeg', 551, 16, 16)

def applyFrame(img_source, frame_img, slice, user_width, user_height, border_width):

	#if prod_img.publisher == '1001':
	#	img_source = Image.open('artevenue/'+settings.STATIC_URL + prod_img.url)			
	#else :
	response = requests.get(img_source.strip())
	user_img = Image.open(BytesIO(response.content))

	# Get the image from the server to extract the frame border
	from django.conf import settings
	path = settings.MOULDING_ROOT + frame_img	

	frame_img = Image.open(path)
	frame_edge = frame_img.crop( (slice, 0, slice + int((frame_img.width-slice) *20/100), slice ) )
	dpi = 0

	inf = frame_edge.info
	
	if 'dpi' in inf:
		dpi = inf['dpi'][0]

	
	width = int(user_img.width)
	height = int(user_img.height)
	
	border = int(border_width * 960 / user_width)
	
	#framepixels = int(user_img.width / user_width)
	framepixels = border
	
	## Create new image with expanded size for the frame
	framed_size = (int(width + framepixels * 2), int(height + framepixels * 2))
	new_img = Image.new("RGB", (framed_size), 0)
	# Paste user image first
	new_img.paste(user_img, (framepixels,framepixels))	
	

	##########################
	## TOP EDGE
	##########################
	# Resize the edge to size of the border required
	frame_top_edge = frame_img.crop( (slice, 0, frame_img.width - slice, slice) )
	percent20 = int(frame_top_edge.width * 20 /100)
	top_edge = frame_top_edge.resize( (int(frame_top_edge.width - percent20), framepixels) )
	for l in range( frame_edge.width - percent20, 20, -percent20):
		top_edge = top_edge.resize((l, framepixels))

	new_img.paste(top_edge, (framepixels,0))

	#***************
	# Repeat border for the TOP EDGE
	#***************
	width_to_fill = int(new_img.width - (framepixels + framepixels))  # corners are already placed
	num_of_imgs = width_to_fill // top_edge.width # number of images that will fit in the edge
	remainder = width_to_fill % top_edge.width # the remainder part

	curr_coord = int(framepixels)
	for l in range( curr_coord, width_to_fill, top_edge.width):
		new_img.paste(top_edge, (l, 0))

	# paste remainder, if any
	if remainder > 0:
		top_rem = top_edge.crop( (top_edge.width - remainder, 0, top_edge.width, top_edge.height) )
		new_img.paste( top_rem, ((width_to_fill + framepixels - remainder), 0))	

	
	##########################
	## TOP RIGHT CORNER
	##########################	
	# Resize the corner to size of the border required
	tr_corner = frame_img.crop( (frame_img.width - slice,0, 
				frame_img.width, slice) )
	top_right_corner = tr_corner.resize((framepixels, framepixels))		
	new_img.paste(top_right_corner, (new_img.width - framepixels, 0))



	##########################
	# RIGHT EDGE
	##########################	
	frame_right_edge = frame_img.crop( (frame_img.width - slice, slice, frame_img.width, slice + int((frame_img.height-slice) *20/100)) )
	percent20 = int(frame_right_edge.height * 20 /100)
	right_edge = frame_right_edge.resize( (framepixels, (int(frame_right_edge.height - percent20))) )
	for l in range( frame_edge.height - percent20, 20, -percent20):
		right_edge = right_edge.resize((framepixels, l))

	height_to_fill = int(new_img.height - framepixels * 2)  # corners are already placed
	remainder = height_to_fill % right_edge.height # the remainder part
	curr_coord = int(framepixels)
	total_pix = 0
	for l in range( curr_coord, height_to_fill + curr_coord - remainder, right_edge.height):
		new_img.paste(right_edge, (new_img.width - framepixels , l))
		total_pix = l

	# paste remainder, if any
	if remainder > 0:
		right_edge_rem = right_edge.crop( (0, 0, right_edge.width, remainder) )
		new_img.paste( right_edge_rem, (new_img.width - framepixels, (height_to_fill + framepixels - remainder)))



	#################
	## BOTTOM EDGE
	#################	
	frame_bottom_edge = frame_img.crop( (slice, frame_img.height - slice, slice + int((frame_img.width-slice) *20/100), frame_img.height ) )
	# Resize the edge to size of the border required
	percent20 = int(frame_bottom_edge.width * 20 /100)
	bottom_edge = frame_bottom_edge.resize( (int(frame_bottom_edge.width - percent20), framepixels) )
	for l in range( frame_bottom_edge.width - percent20, 20, -percent20):
		bottom_edge = bottom_edge.resize((l, framepixels))
	#***************
	# Repeat border for the TOP EDGE
	#***************
	width_to_fill = int(new_img.width - (framepixels + framepixels))  # corners are already placed
	remainder = width_to_fill % bottom_edge.width # the remainder part

	curr_coord = int(framepixels)
	for l in range( curr_coord, width_to_fill, bottom_edge.width):
		new_img.paste(bottom_edge, (l, new_img.height - framepixels))

	# paste remainder, if any
	if remainder > 0:
		bottom_rem = bottom_edge.crop( (bottom_edge.width - remainder, bottom_edge.height - framepixels, bottom_edge.width, bottom_edge.height) )
		new_img.paste( bottom_rem, ((width_to_fill + framepixels - remainder), new_img.height-framepixels))



	##########################
	## BOTTOM RIGHT CORNER
	##########################
	# Resize the bottom right corner to size of the border required
	br_corner = frame_img.crop( (frame_img.width - slice,frame_img.height-slice, 
					frame_img.width, frame_img.height) )
	br_corner = br_corner.resize((framepixels, framepixels))		
	new_img.paste(br_corner, (new_img.width - framepixels, new_img.height - framepixels))
	
	
	
	#######################
	## Bottom Left Corner
	#######################
	# Resize the bottom left corner to size of the border required
	bl_corner = frame_img.crop( (0,frame_img.height-slice, 
					slice, frame_img.height) )
	bl_corner = bl_corner.resize((framepixels, framepixels))		
	new_img.paste(bl_corner, (0, new_img.height - framepixels, framepixels, new_img.height))

	##########################
	# LEFT EDGE
	##########################	
	frame_left_edge = frame_img.crop( (0, slice, slice, slice + int((frame_img.height-slice) *20/100)) )
	percent20 = int(frame_left_edge.height * 20 /100)
	left_edge = frame_left_edge.resize( (framepixels, (int(frame_left_edge.height - percent20))) )
	for l in range( frame_edge.height - percent20, 20, -percent20):
		left_edge = left_edge.resize((framepixels, l))

	height_to_fill = int(new_img.height - framepixels * 2)  # corners are already placed
	remainder = height_to_fill % left_edge.height # the remainder part
	
	curr_coord = int(framepixels)
	for l in range( curr_coord, height_to_fill + curr_coord - remainder, left_edge.height):
		new_img.paste(left_edge, (0 , l))

	# paste remainder, if any
	if remainder > 0:
		left_edge_rem = left_edge.crop( (0,0, left_edge.width, remainder) )
		new_img.paste( left_edge_rem, (0, (height_to_fill + framepixels - remainder)))

	##########################
	## TOP LEFT CORNER
	##########################
	# Resize the bottom right corner to size of the border required
	tl_corner = frame_img.crop( (0,0, slice, slice) )
	tl_corner = tl_corner.resize((framepixels, framepixels))		
	new_img.paste(tl_corner, (0, 0))

	new_img.show()


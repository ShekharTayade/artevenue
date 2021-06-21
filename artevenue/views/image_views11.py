from artevenue.models import Stock_image, Moulding_image, User_image
from artevenue.models import Product_view, Collage_stock_image, Stock_collage
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import messages

from django.http import HttpResponse
from decimal import Decimal
import json

from PIL import Image, ImageFilter

import requests
from io import BytesIO

import base64
from io import StringIO

env = settings.EXEC_ENV
''' Passing image to template
	response = HttpResponse(mimetype="image/png")
	base_image.save(response, "PNG")
	return response
'''

def get_FramedImage(request):
	prod_id = request.GET.get('prod_id', '')
	m_id = request.GET.get('moulding_id', '') 
	mount_color = request.GET.get('mount_color', '') 
	m_size = request.GET.get('mount_size', '0')
	prod_type = request.GET.get('prod_type', 'STOCK-IMAGE')
	stretched_canvas = request.GET.get('stretched_canvas', 'NO')
	imgtilt =  request.GET.get('imgtilt', 'YES')
	dropshadow = request.GET.get('dropshadow', 'YES')
	
	
	if m_size == '' or m_size == '0':
		mount_size = 0
	else:
		mount_size = float(m_size)
		
	u_width = request.GET.get('image_width', '0')
	if u_width == '' or u_width == '0':
		user_width = 0
	else:
		user_width = float(u_width)
		
	prod_type = request.GET.get('prod_type', '') 

	if prod_id == '':
		return HttpResponse('')

	# Get image
	if prod_type == '':
		prod_type = 'STOCK-IMAGE'
	
	prod_img = Product_view.objects.filter( product_id = prod_id,
			product_type_id = prod_type).first()
	
	'''  OPEN FILE FROM A Internet URL '''
	#response = requests.get("http://www.podexchange.com/dsi/lowres/11/11_PSMLT-166_lowres.jpg")
	#if prod_img.publisher == '1001':
	#img_source = Image.open('artevenue/'+settings.STATIC_URL + prod_img.url)			
	env = settings.EXEC_ENV
	if env == 'DEV' or env == 'TESTING':
		if prod_type == 'STOCK-IMAGE' and prod_img.publisher != 'ARTEVENUE':
			response = requests.get(prod_img.url)
			img_source = Image.open(BytesIO(response.content))
		else :
			#img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)			
			img_source = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + prod_img.url)
	else:
		img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)
	
	
	#else :
	#	response = requests.get(prod_img.url)
	#	img_source = Image.open(BytesIO(response.content))

	
	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = m_id, image_type = "APPLY").values(
				'moulding_id', 'url', 'moulding__width_inner_inches', 'border_slice', 'moulding__depth_inches').first()
	
	m_width_inch = None
	
	if moulding:
	
		m_width_inch = float(moulding['moulding__width_inner_inches'])
		
		# Image width displayed in browser in inches
		disp_inch = 450//96
		
		ratio = disp_inch / user_width
		
		## The frame width o the front side
		border = int(m_width_inch * ratio* 96)		
		
		## The frame width on the sides (depth)
		depth = int( float(moulding['moulding__depth_inches']) * ratio * 75 )
		
		m_size = int(mount_size * 96 * ratio)
				
		if m_size > 0 and mount_color != '' and mount_color != '0' and mount_color != 'None':

			img_with_mount = addMount(img_source, mount_color, m_size, m_size, m_size, m_size)
			
			framed_img = applyBorder( request, img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
		else:
			framed_img = applyBorder( request, img_source, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
	else :
		# No moulding, returing the image as it is.
		framed_img = Image.new("RGB", (img_source.width, img_source.height), 0)
		framed_img.paste(img_source, (0,0))

	'''
	response = HttpResponse(content_type="image/png")
	framed_img.save(response, "PNG")
	return response
	#return framed_img
	'''

	if  moulding:
		if imgtilt == 'YES':
			white_frame = False
			if m_id in ('6', '8', '20'):
				white_frame = True
			framed_img = tilt_image(framed_img, border_width = border, frame_flag=True, frame_depth=depth, white_frame = white_frame)
	else:
		## default border width of 30 in case of streched canvas
		border_width = 30
		if stretched_canvas == 'YES':
			if imgtilt == 'YES':
				white_frame = False
				framed_img = tilt_image(framed_img, border_width=border_width, frame_flag=True, white_frame = white_frame)
			elif dropshadow == 'YES':
				framed_img = dropShadow(framed_img, shadow=(0x5F5F5F), iterations=5)
		else:
			if dropshadow == 'YES':
				framed_img = dropShadow(framed_img, shadow=(0x5F5F5F), iterations=5)
	
	buffered = BytesIO()
	framed_img.save(buffered, format='JPEG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)

	return HttpResponse(img_str)
	
def addMount( img_source, mount_color, border_top, border_right, border_bottom, border_left):

	img_source = dropMountShadow( img_source )

	img = Image.new( "RGB", (img_source.width + border_left + border_right, img_source.height + border_top + border_bottom), mount_color)  

	img.paste(img_source, (border_left, border_top))
	
	return img

def applyBorder(request, img_source, ref_url, border_top, border_right, border_bottom, border_left, slice_top, slice_right, slice_bottom, slice_left, m_size = 0, user_width=10):

	# Get the image from the server to extract the frame border
	from django.conf import settings
	path = settings.MOULDING_ROOT + ref_url	

	if m_size > 0:
		gradient_magnitude = 50 / (10 / user_width)
		img_source = dropInnerShadow(img_source, gradient_magnitude)
		
	
	img_ref = Image.open(path)	
	
	box_topleftcorner = (0, 0, slice_left, slice_top)

	topleftcorner = img_ref.crop(box_topleftcorner)
	topleftcorner = topleftcorner.resize((border_left, border_top))
	
	box_topedge = (slice_left, 0, img_ref.width - slice_right, slice_top)
	topedge = img_ref.crop(box_topedge)
	topedge = topedge.resize((topedge.width, border_top))
	
	box_toprightcorner = (img_ref.width - slice_right, 0, img_ref.width, slice_top)
	toprightcorner = img_ref.crop(box_toprightcorner)
	toprightcorner = toprightcorner.resize((border_right, border_top))

	box_rightedge = (img_ref.width - slice_right, slice_top, img_ref.width, img_ref.height - slice_bottom)
	rightedge = img_ref.crop(box_rightedge)
	rightedge = rightedge.resize((border_right, rightedge.height))
	
	box_bottomrightcorner = (img_ref.width - slice_right, img_ref.height - slice_bottom, img_ref.width, img_ref.height)
	bottomrightcorner = img_ref.crop(box_bottomrightcorner)
	bottomrightcorner = bottomrightcorner.resize((border_right, border_bottom))
	

	box_bottomedge = (slice_left, img_ref.height - slice_bottom, img_ref.width - slice_right, img_ref.height)
	bottomedge = img_ref.crop(box_bottomedge)
	bottomedge = bottomedge.resize((bottomedge.width, border_bottom))
	
	box_bottomleftcorner = (0, img_ref.height - slice_bottom, slice_left, img_ref.height)
	bottomleftcorner = img_ref.crop(box_bottomleftcorner)
	bottomleftcorner = bottomleftcorner.resize((border_left, border_bottom))

	box_leftedge = (0, slice_top, slice_left, img_ref.height - slice_bottom)
	leftedge = img_ref.crop(box_leftedge)
	leftedge = leftedge.resize((border_left, leftedge.height))
	# drop shadow for left edge
	#leftedge = dropShadow(leftedge, shadow=(0x00,0x00,0x00,0xff))
	#leftedge = dropFrameShadowIn(leftedge)
	
	new_img = Image.new("RGB", (img_source.width + border_left + border_right, img_source.height + border_top + border_bottom), 0)

	new_img.paste(img_source, (border_left,border_top)) 	# paste the image to apply the border to
	
	'''***************
	Repeat border for the TOP EDGE
	'''
	width_to_fill = int(new_img.width - (border_left + border_right))  # corners are already placed
	num_of_imgs = width_to_fill // topedge.width # number of images that will fit in the edge
	remainder = width_to_fill % topedge.width # the remainder part

	curr_coord = int(border_left)
	for l in range( curr_coord, width_to_fill, topedge.width):
		new_img.paste(topedge, (l, 0))

	# paste remainder, if any
	if remainder > 0:
		top_rem = topedge.crop( (topedge.width - remainder, 0, topedge.width, topedge.height) )
		new_img.paste( top_rem, ((width_to_fill + border_left - remainder), 0))	

	'''***************
	Repeat border for the BOTTOM EDGE
	'''
	width_to_fill = int(new_img.width - (border_left + border_right))  # corners are already placed
	num_of_imgs = width_to_fill // bottomedge.width # number of images that will fit in the edge
	remainder = width_to_fill % bottomedge.width # the remainder part

	curr_coord = int(border_left)
	for l in range( curr_coord, width_to_fill, bottomedge.width):
		new_img.paste(bottomedge, (l, new_img.height - border_bottom))


	# paste remainder, if any
	if remainder > 0:
		bottom_rem = bottomedge.crop( (bottomedge.width - remainder, 0, topedge.width, bottomedge.height) )
		new_img.paste( bottom_rem, ((width_to_fill + border_left - remainder), new_img.height - border_bottom))

	'''***************
	Repeat border for the LEFT EDGE
	'''
	height_to_fill = int(new_img.height - (border_top + border_bottom))  # corners are already placed
	num_of_imgs = height_to_fill // leftedge.height # number of images that will fit in the edge
	
	curr_coord = int(border_top)
	if leftedge.height >= height_to_fill:
		leftedge = leftedge.crop( (0, 0, leftedge.width, height_to_fill) )
		
	remainder = height_to_fill % leftedge.height # the remainder part

	for l in range( curr_coord, height_to_fill, leftedge.height):
		new_img.paste(leftedge, (0, l))

	# paste remainder, if any
	if remainder > 0:
		left_rem = leftedge.crop( (0, 0, leftedge.width, remainder) )
		new_img.paste( left_rem, (0, (height_to_fill + border_bottom - remainder)) )
	
	'''***************
	Repeat border for the RIGHT EDGE
	'''
	height_to_fill = int(new_img.height - (border_top + border_bottom))  # corners are already placed
	num_of_imgs = height_to_fill // rightedge.height # number of images that will fit in the edge
	remainder = height_to_fill % rightedge.height # the remainder part

	curr_coord = int(border_top)
	for l in range( curr_coord, height_to_fill, rightedge.height):
		new_img.paste(rightedge, (new_img.width - border_right, l))

	
	# paste remainder, if any
	if remainder > 0:
		right_rem = rightedge.crop( (0, rightedge.height - remainder, rightedge.width, rightedge.height) )
		new_img.paste( right_rem, ( new_img.width - border_right, height_to_fill + border_bottom - remainder) )
	

	new_img.paste(topleftcorner, (0,0))
	#new_img.paste(topedge, (border_left,0))
	new_img.paste(toprightcorner, (new_img.width - border_right, 0))
	#new_img.paste(rightedge, (new_img.width - border_right, border_top))
	new_img.paste(bottomrightcorner, (new_img.width - border_right, new_img.height - border_bottom))
	#new_img.paste(bottomedge, (border_left, new_img.height - border_bottom) )
	new_img.paste(bottomleftcorner, (0, new_img.height - border_bottom))
	#new_img.paste(leftedge, (0, border_top))

	
	return new_img
	
''' Apply all mouldings to the given product image ''' 
def get_ImagesWithAllFrames(request, prod_id, user_width):
	# Get image
	prod_img = Stock_image.objects.filter( product_id = prod_id ).first()
	
	'''  OPEN FILE FROM A Internet URL '''
	img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)			
	
	# Get all mouldings
	moulding = Moulding_image.objects.filter(image_type = "APPLY").values(
				'url', 'moulding__width_inner_inches', 'border_slice')
	

	# Image width displayed in browser in inches
	disp_inch = 450//96
	
	ratio = disp_inch / user_width
	
	## The frame width o the front side
	border = int(m_width_inch * ratio* 96)		
	
	## The frame width on the sides (depth)
	depth = int( float(moulding['moulding__depth_inches']) * ratio * 75 )
	
	m_size = int(mount_size * 96 * ratio)
	
	frames_array = []
	
	import traceback
	try:
		for m in moulding:
			m_width_inch = float(m['moulding__width_inner_inches'])
			border = int(m_width_inch * ratio * 96)

			framed_img = applyBorder( request, img_source, m['url'], border, border, border, border,
							float(m['border_slice']), float(m['border_slice']), 
							float(m['border_slice']), float(m['border_slice']), m_size, user_width)

			buffered = BytesIO()
			framed_img.save(buffered, format='JPEG')
			img_data = buffered.getvalue()
			img_str = base64.b64encode(img_data)

			frames_array.append(img_str)
	except :
			print(traceback.format_exc())
			
	return frames_array
	
def get_FramedUserImage(request):

	m_id = request.GET.get('moulding_id', '') 
	mount_color = request.GET.get('mount_color', '') 
	mount_size = float(request.GET.get('mount_size', '0'))
	user_width = float(request.GET.get('image_width', '0'))

	# Get the user image
	session_id = request.session.session_key
	user = None
	
	if request.user.is_authenticated:
		try:
			user = User.objects.get(username = request.user)
			user_image = User_image.objects.filter(user = user, status = "INI").first()
		except User.DoesNotExist:
			user = None
	else:
		if session_id is None:
			request.session.create()
			session_id = request.session.session_key
		user_image = User_image.objects.filter(session_id = session_id, status = "INI").first()
	
	if not user_image:
		return HttpResponse('')
	
	img_source=Image.open(user_image.image_to_frame)
	
	# We have to resize the image to base width of 450px. As the user image would be bigger
	# size and our ratio of onscreen display with mount,frame would be inappropriate visually.
	basewidth = 1000 
	wpercent = (basewidth/float(img_source.size[0]))
	hsize = int((float(img_source.size[1])*float(wpercent)))
	img_to_frame = img_source.resize((basewidth,hsize), Image.ANTIALIAS)

	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = m_id, image_type = "APPLY").values(
				'url', 'moulding__width_inner_inches', 'border_slice').first()
	
	if moulding:
	
		m_width_inch = float(moulding['moulding__width_inner_inches'])
		
		# Image width displayed in browser in inches
		disp_inch = 450//96
		
		ratio = disp_inch / user_width
		
		border = int(m_width_inch * ratio * 96)
		
		border = int(m_width_inch * 450 / user_width)
		
		m_size = int(mount_size * 96 * ratio)
		if m_size > 0 and mount_color != '' and mount_color != '0' and mount_color != 'None':

			img_with_mount = addMount(img_to_frame, mount_color, m_size, m_size, m_size, m_size)
			
			framed_img = applyBorder( request, img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
		else:
			framed_img = applyBorder( request, img_to_frame, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
	else :
		# No moulding, returing the image as it is.
		framed_img = Image.new("RGB", (img_source.width, img_source.height), 0)
		framed_img.paste(img_source, (0,0))		
	'''
	response = HttpResponse(content_type="image/png")
	framed_img.save(response, "PNG")
	return response
	#return framed_img
	'''
	##framed_img = dropShadow(framed_img)

	buffered = BytesIO()
	framed_img.save(buffered, format='JPEG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)


	return HttpResponse(img_str)
	
def get_FramedUserImage_by_id(request):

	user_image_id = request.GET.get('user_image_id', '0')
	m_id = request.GET.get('moulding_id', '') 
	mount_color = request.GET.get('mount_color', '') 
	mount_size = float(request.GET.get('mount_size', '0'))
	user_width = float(request.GET.get('image_width', '0'))

	# Get the user image
	session_id = request.session.session_key
	user = None
	
	if request.user.is_authenticated:
		try:
			user = User.objects.get(username = request.user)
			user_image = User_image.objects.filter(user = user, id = user_image_id).first()
		except User.DoesNotExist:
			user = None
	else:
		if session_id is None:
			request.session.create()
			session_id = request.session.session_key
		user_image = User_image.objects.filter(session_id = session_id, id = user_image_id).first()
	
	if not user_image:
		return HttpResponse('')
	
	img_source=Image.open(user_image.image_to_frame)
	
	# We have to resize the image to base width of 450px. As the user image would be bigger
	# size and our ratio of onscreen display with mount,frame would be inappropriate visually.
	basewidth = 1000 
	wpercent = (basewidth/float(img_source.size[0]))
	hsize = int((float(img_source.size[1])*float(wpercent)))
	img_to_frame = img_source.resize((basewidth,hsize), Image.ANTIALIAS)

	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = m_id, image_type = "APPLY").values(
				'moulding_id', 'url', 'moulding__width_inner_inches', 'border_slice').first()
	
	if moulding:
	
		m_width_inch = float(moulding['moulding__width_inner_inches'])
		
		# Image width displayed in browser in inches
		disp_inch = 450//96
		
		ratio = disp_inch / user_width
		
		border = int(m_width_inch * ratio * 96)
		
		border = int(m_width_inch * 450 / user_width)
		
		m_size = int(mount_size * 96 * ratio)
		if m_size > 0 and mount_color != '' and mount_color != '0' and mount_color != 'None':

			img_with_mount = addMount(img_to_frame, mount_color, m_size, m_size, m_size, m_size)
			
			framed_img = applyBorder( request, img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
		else:
			framed_img = applyBorder( request, img_to_frame, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
	else :
		# No moulding, returing the image as it is.
		framed_img = Image.new("RGB", (img_source.width, img_source.height), 0)
		framed_img.paste(img_source, (0,0))		
	'''
	response = HttpResponse(content_type="image/png")
	framed_img.save(response, "PNG")
	return response
	#return framed_img
	'''
	framed_img = dropShadow(framed_img)

	buffered = BytesIO()
	framed_img.save(buffered, format='JPEG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)


	return HttpResponse(img_str)

def dropShadow( image, offset=(8,8), background=0xffffff, shadow=0xc3c3c3, 
                border=10, iterations=7):
	"""
	Add a gaussian blur drop shadow to an image.  

	image       - The image to overlay on top of the shadow.
	offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
				positive or negative.
	background  - Background colour behind the image.
	shadow      - Shadow colour (darkness).
	border      - Width of the border around the image.  This must be wide
				enough to account for the blurring of the shadow.
	iterations  - Number of times to apply the filter.  More iterations 
				produce a more blurred shadow, but increase processing time.
	"""

	# Create the backdrop image -- a box in the background colour with a 
	# shadow on it.
	totalWidth = image.size[0] + abs(offset[0]) + 2*border
	totalHeight = image.size[1] + abs(offset[1]) + 2*border

	back = Image.new(image.mode, (totalWidth, totalHeight), background)

	# Place the shadow, taking into account the offset from the image
	shadowLeft = border + max(offset[0], 0)
	shadowTop = border + max(offset[1], 0)
	back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], shadowTop + image.size[1]] )
  
	# Apply the filter to blur the edges of the shadow.  Since a small kernel
	# is used, the filter must be applied repeatedly to get a decent blur.
	n = 0
	#while n < iterations:
	#	back = back.filter(ImageFilter.BLUR)
	#	n += 1
    
	back = back.filter(ImageFilter.GaussianBlur(radius=7))
	
	# Paste the input image onto the shadow backdrop  
	imageLeft = border - min(offset[0], 0)
	imageTop = border - min(offset[1], 0)
	back.paste(image, (imageLeft, imageTop))

	return back
    	
def dropFrameShadowIn(image, shadowWidth=6, color=0x444444, shadow=0x999999):


	totalWidth = image.size[0] + (shadowWidth)
	totalHeight = image.size[1]
	img = Image.new(image.mode, (totalWidth, totalHeight), '#999999')
	shadow_black = Image.new(image.mode, (6, totalHeight), '#000000')
	#shadow1 = Image.new(image.mode, (2, totalHeight), '#444444')
	#shadow2 = Image.new(image.mode, (3, totalHeight), '#666666')
	
	img.paste(shadow_black, (image.size[0], 0))
	#img.paste(shadow1, (image.size[0] + 1, 0))	
	#img.paste(shadow2, (image.size[0] + 3, 0))	
	n = 0
	while n < 3:
		img = img.filter(ImageFilter.BLUR)
		n += 1
	img.paste(image)
	#img.paste(shadow_black, (image.size[0], 0))
	return img
	

def get_FramedImage_by_id(request, prod_id, m_id, mount_color='', 
		mount_size=0, user_width=0, prod_type='STOCK-IMAGE', stretched_canvas='NO', imgtilt='NO', dropshadow='NO' ):	
	if not prod_id:
		if prod_id == '':
			return HttpResponse('')	
	if not m_id:
		if m_id == '':
			return HttpResponse('')							
	if prod_id == '':
		return HttpResponse('')
	# Get image
	if prod_type == '':
		prod_type = 'STOCK-IMAGE'

	prod_img = Product_view.objects.filter( product_id = prod_id,
			product_type_id = prod_type).first()
	
	env = settings.EXEC_ENV
	
	if env == 'DEV' or env == 'TESTING':
		if prod_type == 'STOCK-IMAGE' and prod_img.publisher != 'ARTEVENUE':
			response = requests.get(prod_img.url)
			img_source = Image.open(BytesIO(response.content))
		else :
			img_source = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + prod_img.url)
	else:
		img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)
		
	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = m_id, image_type = "APPLY").values(
				'moulding_id', 'url', 'moulding__width_inner_inches', 'border_slice').first()
	
	if moulding:	
		m_width_inch = float(moulding['moulding__width_inner_inches'])
		
		# Image width displayed in browser in inches
		disp_inch = 450//96
		
		ratio = disp_inch / user_width
		
		border = int(m_width_inch * ratio* 96)		
		#border = int(m_width_inch * 96/ user_width)
		
		m_size = int(mount_size * 96 * ratio)
		#m_size = int(mount_size * 960 / user_width)
		
		if m_size > 0 and mount_color != '' and mount_color != '0' and mount_color != 'None':

			img_with_mount = addMount(img_source, mount_color, m_size, m_size, m_size, m_size)
			
			framed_img = applyBorder( request, img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
		else:
			framed_img = applyBorder( request, img_source, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']), m_size, user_width )
	else :
		# No moulding, returing the image as it is.
		framed_img = Image.new("RGB", (img_source.width, img_source.height), 0)
		framed_img.paste(img_source, (0,0))		


	if  moulding:
		if m_width_inch < 1:
			border_width = border
		else:
			border_width = border
		
		white_frame = False
		if m_id in ('6', '8', '20'):
			white_frame = True
		if imgtilt == 'YES':
			framed_img = tilt_image(framed_img, border_width = border_width, flag=True, white_frame = white_frame)
		
		if dropshadow == 'YES':
			framed_img = dropShadow(framed_img, shadow=(0x5F5F5F), iterations=5)
	else:
		## default border width of 30 in case of streched canvas
		border_width = 30
		if stretched_canvas == 'YES':
			white_frame = False
			if imgtilt == 'YES':				
				framed_img = tilt_image(framed_img, border_width=border_width, flag=True)
			elif dropshadow == 'YES':
				framed_img = tilt_image(framed_img, border_width=border_width, flag=True)
		else:
			if dropshadow == 'YES':
				framed_img = dropShadow(framed_img, shadow=(0x5F5F5F), iterations=5)
	
	##framed_img = dropShadow(framed_img)
	'''
	buffered = BytesIO()
	framed_img.save(buffered, format='JPEG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)

	return HttpResponse(img_str)
	'''
	return framed_img


@csrf_exempt
def get_catalog_card(request, return_img_str=True):

	card_no = request.GET.get('card_no', '')
	prod_id = request.GET.get('prod_id', '')
	m_id = request.GET.get('moulding_id', '')
	mount_color = request.GET.get('mount_color', '0')
	mount_size = float(request.GET.get('mount_size', '0'))
	user_width = float(request.GET.get('image_width', '0'))
	prod_type = request.GET.get('prod_type', '')

	## Fixing this display size to 20 inch for the display on cards.
	user_width = 15
	
	prod = Stock_image.objects.get(product_id = prod_id)

	if card_no == '1':
	
		if float(prod.aspect_ratio) >= 0.8:
			## 165, 125		635,450
			#card = get_catalog(request, False, 'roomview_1.jpg', 225, 135, 380, 290, prod_id, m_id, mount_color,
			#		mount_size, user_width, prod_type, card_no, False)
					
			## 250, 115, 380, 285
			card = get_catalog(request, False, 'roomview_4.jpg', 270, 145, 300, 245, prod_id, m_id, mount_color,
					mount_size, user_width, prod_type, card_no, False)
			
		else:
			## 245, 85	290, 420
			card = get_catalog(request, False, 'roomview_1_v.jpg', 275, 85, 320, 420, prod_id, m_id, mount_color,
					mount_size, user_width, prod_type, card_no, False)		
					
	if card_no == '2':
		## 350, 115		480,470
		#card = get_catalog(request, False, 'roomview_2.jpg', 265, 75, 350, 315, prod_id, m_id, mount_color,
		#		mount_size, user_width, prod_type, card_no, False)
		card = get_catalog(request, False, 'card_dynamic.jpg', 665, 230, 750, 750, prod_id, m_id, mount_color,
				mount_size, user_width, prod_type, card_no, False)

	if card_no == '3':
	
		if float(prod.aspect_ratio) >= 0.8:
			## 235, 95, 380, 265235, 95, 380, 265
			card = get_catalog(request, False, 'roomview_3.jpg', 245, 140, 368, 210, prod_id, m_id, mount_color,
					mount_size, user_width, prod_type, card_no, False)
		else:
			## 260, 60, 340, 320
			card = get_catalog(request, False, 'roomview_3_v.jpg', 260, 60, 340, 320, prod_id, m_id, mount_color,
					mount_size, user_width, prod_type, card_no, False)

	if card_no == '4':
		card = get_catalog(request, False, 'feature_2_1.jpg', 357, 349, 609, 579, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no, False)

	if card_no == '5':
		card = get_catalog(request, True, 'feature_1_1.jpg', 0, 105, 550, 760, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no, False)


	if card_no == 'AMZ_C1':
		card = get_catalog(request, False, 'feature_1_amz.jpg', 315, 80, 580, 510, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no, False)


	'''
	if card_no == '1':
		#card = get_catalog(request, True, 'feature_1.jpg', 0, 105, 550, 760, prod_id, m_id, mount_color, 
		#		mount_size, user_width, prod_type, card_no)
		card = get_catalog(request, True, 'feature_1_1.jpg', 0, 105, 550, 760, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)
				
	if card_no == '2':
		card = get_catalog(request, True, 'feature_2.jpg', 500, 165, 500, 625, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)
				
	if card_no == '3':
		#card = get_catalog(request, False, 'feature_3.jpg', 145, 190, 470, 590, prod_id, m_id, mount_color, 
		#		mount_size, user_width, prod_type, card_no)		
		card = get_catalog(request, False, 'feature_2_1.jpg', 357, 349, 609, 579, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)		

	if card_no == '4':
		#card = get_catalog(request, False, 'catalog_3_1.jpg', 195, 165, 515, 315, prod_id, m_id, mount_color, 
		#		mount_size, user_width, prod_type, card_no)
		card = get_catalog(request, False, 'catalog_3_1.jpg', 165, 7, 579, 519, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no, True)

	if card_no == '5':
		card = get_catalog(request, False, 'catalog_2.jpg', 220, 85, 300, 160, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)

	if card_no == '6':
		#card = get_catalog(request, False, 'catalog_4.jpg', 156, 75, 405, 235, prod_id, m_id, mount_color, 
		#		mount_size, user_width, prod_type, card_no)
		card = get_catalog(request, False, 'catalog_4_1.jpg', 36, 17, 678, 341, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no, True)

	'''
	
	if return_img_str:
		buffered = BytesIO()
		card.save(buffered, format='JPEG')
		card = buffered.getvalue()
		img_str = base64.b64encode(card)
		
		return HttpResponse(img_str)
	else:
		return card
	
def get_catalog(request, crop_half, file_nm, x, y, max_w, max_h, prod_id, m_id, mount_color='', 
		mount_size=0, user_width=0, prod_type='STOCK-IMAGE', card_no=1, size_perps = False):
		
	img = get_FramedImage_by_id(request, prod_id, m_id, mount_color, 
			mount_size, user_width, prod_type, dropshadow="NO")

	ratio = img.width / img.height

	### Resize image proportionate to the room objects in the catalog image
	'''
	if card_no == '4':
		pixel_w = round(500 / 54 * user_width + 4 )
		pixel_h = int(pixel_w / ratio)
		img = img.resize( (pixel_w, pixel_h) )
	'''
	
	if crop_half:
		img_w = img.width
		img_h = img.height		
		img = img.crop((0, 0, round(img_w/2), img_h))		
		

	###########################################
	## Resize image width, height of the image
	## as per available space
	###########################################
	w = img.width
	h = img.height
	ratio = img.width / img.height
	
	########################### This code sets the size proportionately on catalog card 
	if size_perps:
		moulding = Moulding_image.objects.get(moulding_id = m_id, image_type = "APPLY")
		## Actual user width
		u_width = user_width + mount_size * 2 + float(moulding.moulding.width_inner_inches) * 2
		## For dsplay purpose
		w = round(u_width * 8.33 )
		h = round(w / ratio)
	
	###########################
	
	if w > max_w:
		w = max_w
		h = int(max_w / ratio)
	if h > max_h:
		h = max_h
		w = int(max_h * ratio)
	img = img.resize((w, h))

	env = settings.EXEC_ENV
	if env == 'DEV' or env == 'TESTING':	
		catalog_img = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/catalog/' + file_nm)
	else:
		catalog_img = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL  + 'img/catalog/' + file_nm)

	##img = dropShadow_transparent_background(img,shadow=(0x00,0x00,0x00,0xff))

	if img.width < max_w:
		gap_w = max_w - img.width 
		x = x + round(gap_w / 2)
	if img.height < max_h:
		gap_h = max_h - img.height 
		y = y + round(gap_h / 2)

	catalog_img.paste(img, (x, y))

	return catalog_img

@csrf_exempt
def get_collage_catalog_card(request):
	card_no = request.GET.get('card_no', '')
	prod_id = request.GET.get('prod_id', '')
	m_id = request.GET.get('moulding_id', '')
	mount_color = request.GET.get('mount_color', '0')
	mount_size = float(request.GET.get('mount_size', '0'))
	user_width = float(request.GET.get('image_width', '0'))
	prod_type = request.GET.get('prod_type', '')

	## Fixing this display size to 20 inch for the display on cards.
	user_width = 15
	
	if card_no == '1':
		'''
		## 15, 125, 815, 285
		card = get_collage_catalog(request, False, 'roomview_1_set.jpg', 15, 125, 815, 285, prod_id, m_id, mount_color,
				mount_size, user_width, prod_type, card_no, False)		
		'''
		##65, 110, 710, 225
		card = get_collage_catalog(request, False, 'roomview_1_set1.jpg', 65, 110, 710, 225, prod_id, m_id, mount_color,
				mount_size, user_width, prod_type, card_no, False)		

	if card_no == '2':
		## 105, 165, 730, 245
		card = get_collage_catalog(request, False, 'roomview_2_set.jpg', 105, 165, 730, 245, prod_id, m_id, mount_color,
				mount_size, user_width, prod_type, card_no, False)

	if card_no == '3':
		## 195, 170, 510, 160
		card = get_collage_catalog(request, False, 'roomview_3_set.jpg', 195, 170, 510, 160, prod_id, m_id, mount_color,
				mount_size, user_width, prod_type, card_no, False)

	if card_no == '4':
		card = get_collage_catalog(request, False, 'feature_2_1.jpg', 357, 349, 609, 579, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no, False)

	if card_no == '5':
		card = get_collage_catalog(request, True, 'feature_1_1.jpg', 0, 105, 550, 760, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no, False)

	'''
	if card_no == '6':
		card = get_collage_catalog(request, False, 'catalog_4.jpg', 105, 105, 515, 200, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)

	if card_no == '4':
		card = get_collage_catalog(request, False, 'catalog_3.jpg', 190, 225, max_h, 235, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)

	if card_no == '3':
		#card = get_collage_catalog(request, False, 'feature_3.jpg', 20, 330, 650, 315, prod_id, m_id, mount_color, 
		#		mount_size, user_width, prod_type, card_no)		
		card = get_collage_catalog(request, False, 'feature_2_1.jpg', 357, 349, 609, 579, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)		

	if card_no == '1':
		#card = get_collage_catalog(request, True, 'feature_1.jpg', 0, 295, 610, 395, prod_id, m_id, mount_color, 
		#		mount_size, user_width, prod_type, card_no)
		card = get_collage_catalog(request, True, 'feature_1_1.jpg', 0, 105, 550, 760, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)

	if card_no == '2':
		card = get_collage_catalog(request, True, 'feature_2.jpg', 405, 315, 590, 330, prod_id, m_id, mount_color, 
				mount_size, user_width, prod_type, card_no)

	'''
	
	buffered = BytesIO()
	card.save(buffered, format='JPEG')
	card = buffered.getvalue()
	img_str = base64.b64encode(card)
	
	return HttpResponse(img_str)

def get_collage_catalog(request, crop_half, file_nm, x, y, max_w, max_h, prod_id, m_id, mount_color='', 
		mount_size=0, user_width=0, prod_type='STOCK-COLLAGE', card_no=1, size_perps = False):
		
	env = settings.EXEC_ENV
	if env == 'DEV' or env == 'TESTING':	
		catalog_img = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/catalog/' + file_nm)
	else:
		catalog_img = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL  + 'img/catalog/' + file_nm)
	
	coll = Collage_stock_image.objects.filter(stock_collage_id = prod_id)

		
	## Get all images
	px = x
	py = y
	img = []
	### Get framed image for each
	for c in coll:
		img.append( get_FramedImage_by_id(request, c.stock_image_id, m_id, mount_color, 
						mount_size, user_width, 'STOCK-IMAGE') )
						
	## Resize each image to fit in the card
	total_w = 20
	img_arr = []
	total_h = 0
	for i in img:
		w = round((max_w / c.stock_collage.set_of) - 60)
		
		# reduce size by 30% in case of set of 2
		if c.stock_collage.set_of == 2:
			w =  round(w - (w * 0.3) )
		
		h = round(w / c.stock_image.aspect_ratio)
		if h > max_h:
			h = max_h
			w = h * c.stock_image.aspect_ratio
		total_h = h
				
		i = i.resize((w, h))
		img_arr.append(i)
		total_w = total_w + i.width + 20
	
	## Paste each image on to the card
	w_gap = max_w - total_w
	h_gap = max_h - total_h
	px = round(px + w_gap /2) + 20
	py = round(py + h_gap /2)
	for i in img_arr:			
		catalog_img.paste(i, (px, py))
		px = px + i.width + 20
		
	return catalog_img


def decode_base64_file(data):

	def get_file_extension(file_name, decoded_file):
		import imghdr

		extension = imghdr.what(file_name, decoded_file)
		extension = "jpg" if extension == "jpeg" else extension

		return extension

	from django.core.files.base import ContentFile
	import base64
	import six
	import uuid

	# Check if this is a base64 string
	if isinstance(data, six.string_types):
		# Check if the base64 string is in the "data:" format
		if 'data:' in data and ';base64,' in data:
			# Break out the header from the base64 content
			header, data = data.split(';base64,')

		# Try to decode the file. Return validation error if it fails.
		try:
			decoded_file = base64.b64decode(data)
		except TypeError:
			TypeError('invalid_image')

		# Generate file name:
		file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
		# Get the file name extension:
		file_extension = get_file_extension(file_name, decoded_file)

		complete_file_name = "%s.%s" % (file_name, file_extension, )

		return ContentFile(decoded_file, name=complete_file_name)

def change_pixel_color(img_file, color):
	img = Image.open(img_file)
	img = img.convert("RGBA")
	pixdata = img.load()
	 
	# Clean the background noise, if color != white, then set to black.
	for y in range(img.size[1]):
		for x in range(img.size[0]):
			if pixdata[x, y] == (255,255,255,255):
				#pixdata[x, y] = (255, 0, 0, 255)
				pixdata[x, y] = color

	img.show()
	img.save('output.png')
	

@csrf_exempt
def show_on_wall(request):

	i_color = request.POST.get('color', '')
	wall_file_nm = i_color.replace(',','-')
	i_color = i_color.split(',')
	l_color = []
	for i in i_color:
		l_color.append(int(i))
		
	color = tuple(l_color)
	
	'''
	img_str = request.POST.get('img_str', '')
	img_str = img_str.replace('data:image/png;base64,', '')
    '''                           
	prod_id = request.POST.get('prod_id', '')
	m_id = request.POST.get('moulding_id', '')
	mount_color = request.POST.get('mount_color', '0')
	mount_size = float(request.POST.get('mount_size', '0'))
	user_width = float(request.POST.get('image_width', '0'))	
	
	'''
	imgdata = base64.b64decode(img_str)

	from django.utils.crypto import get_random_string
	if env == 'DEV' or env == 'TESTING':	
		filename = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'tmp/' + get_random_string(8).lower() + ".jpg"
	else:
		filename = settings.PROJECT_DIR + '/' + settings.STATIC_URL  + 'tmp/' + get_random_string(8).lower() + ".jpg"

	with open(filename, 'wb') as f:
		f.write(imgdata)	
	
	'''
	img = get_FramedImage_by_id(request, prod_id, m_id, mount_color, 
				mount_size, user_width, 'STOCK-IMAGE')	
				
	#painting = Image.open(filename)
	
	painting = img
	
	if env == 'DEV' or env == 'TESTING':
		img = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + "img/catalog/wall-" + wall_file_nm + ".jpg")
	else:
		img = Image.open(settings.PROJECT_DIR + "/" + settings.STATIC_URL + "img/catalog/wall-" + wall_file_nm + ".jpg")

	img = img.convert("RGBA")
	pixdata = img.load()
	 
	# if color != white, then set to given color.
	'''
	for y in range(img.size[1]):
		for x in range(img.size[0]):
			if pixdata[x, y] == (0, 168, 243):
				pixdata[x, y] = color
	'''
	ratio = painting.width / painting.height
	########################### This code sets the size proportionately on catalog card 
	try:
		moulding = Moulding_image.objects.get(moulding_id = m_id, image_type = "APPLY")
		## Actual user width
		u_width = user_width + mount_size * 2 + float(moulding.moulding.width_inner_inches) * 2
	except Moulding_image.DoesNotExist:
		u_width = user_width

	
	## For display purpose
	#w = round(u_width * 16.66 )
	w = round(u_width * 10.4 )
	h = round(w / ratio)
	###########################
	
	x = 50
	y = 40
	max_w = 765
	max_h = 425
	
	size_crossed = False
	if w > max_w:
		size_crossed = True
		w = max_w
		h = int(max_w / ratio)
	if h > max_h:
		size_crossed = True
		h = max_h
		w = int(max_h * ratio)
	painting = painting.resize((w, h))

	if painting.width < max_w:
		gap_w = max_w - painting.width 
		x = x + round(gap_w / 2)
	if painting.height < max_h:
		gap_h = max_h - painting.height 
		y = y + round(gap_h / 2)

	img.paste(painting, (x, y))
	img.resize( (850, round(850/ratio)) )
	
	buffered = BytesIO()
	img.save(buffered, format='PNG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)

	response = HttpResponse(img_str)
	if (size_crossed == True):
		response.set_cookie(key='size_crossed', value=1)
	else:
		response.set_cookie(key='size_crossed', value=0)
	
	return response
	
@csrf_exempt
def show_on_wall_set(request):

	i_color = request.POST.get('color', '')
	wall_file_nm = i_color.replace(',','-')
	i_color = i_color.split(',')
	l_color = []
	for i in i_color:
		l_color.append(int(i))
		
	color = tuple(l_color)
	
	prod_id = request.POST.get('prod_id', '')
	m_id = request.POST.get('moulding_id', '')
	mount_size = float(request.POST.get('mount_size', '0'))
	user_width = float(request.POST.get('image_width', '0'))
	mount_color = request.POST.get('mount_color', '0')
	
	coll = Collage_stock_image.objects.filter(stock_collage_id = prod_id)

	#x = 30
	#y = 185
	#max_w = 820
	#max_h = 220
	max_w = 600 
	max_h = 450
	x = 137
	y = 50
	
	try:
		moulding = Moulding_image.objects.get(moulding_id = m_id, image_type = "APPLY")
		## Actual user width
		u_width = user_width + mount_size * 2 + float(moulding.moulding.width_inner_inches) * 2
	except Moulding_image.DoesNotExist:
		u_width = user_width

	#img = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + "img/catalog/wall-" + wall_file_nm + ".jpg")
	if env == 'DEV' or env == 'TESTING':
		img = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + "img/catalog/wall-" + wall_file_nm + ".jpg")
	else:
		img = Image.open(settings.PROJECT_DIR + "/" + settings.STATIC_URL + "img/catalog/wall-" + wall_file_nm + ".jpg")
	
	img = img.convert("RGBA")
	pixdata = img.load()

	## Get all images
	px = x
	py = y
	imgs = []	
	### Get framed image for each
	for c in coll:
		i = get_FramedImage_by_id(request, c.stock_image_id, m_id, mount_color, 
				mount_size, u_width, 'STOCK-IMAGE')		
		imgs.append(i)
		
	size_crossed = False		

	## Resize each image to fit in the card
	total_w = 20
	img_arr = []
	total_h = 0
	for i in imgs:
		## For display purpose
		w = round(u_width * 10.4 )
		h = round(w / (i.width/i.height) )
		
		if h > max_h:
			size_crossed = True
			h = max_h
			w = round(h * (i.width/i.height))
		total_h = h
				
		i = i.resize((w, h))
		img_arr.append(i)
		total_w = total_w + i.width + 20

	
	## Paste each image on to the card
	w_gap = max_w - total_w
	h_gap = max_h - total_h
	px = round(px + w_gap /2) + 20
	py = round(py + h_gap /2)
	for i in img_arr:			
		img.paste(i, (px, py))
		px = px + i.width + 20

	ratio = img.width / img.height
	
	img.resize( (850, round(850/ratio)) )
	
	buffered = BytesIO()
	img.save(buffered, format='PNG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)

	response = HttpResponse(img_str)
	if (size_crossed == True):
		response.set_cookie(key='size_crossed', value=1)
	else:
		response.set_cookie(key='size_crossed', value=0)
	
	return response
	
	
def test_wall(p_id, width):

	from django.http import HttpRequest
	request = HttpRequest()
	
	framed_img = get_FramedImage_by_id(request, p_id, 18, '#fff', 
		1, width, 'STOCK-IMAGE' )

	buffered = BytesIO()
	framed_img.save(buffered, format='JPEG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)

	show_on_wall(img_str, (137,46,58,255), 14)
	
def test_shadow():
	prod_id = '153111'
	m_id = 26
	mount_color = '#fff'
	m_size = '1'
	prod_type = 'STOCK-IMAGE'	

	from django.http import HttpRequest
	request = HttpRequest()

	if m_size == '' or m_size == '0':
		mount_size = 0
	else:
		mount_size = float(m_size)
		
	u_width = '10'

	user_width = float(u_width)

	prod_img = Product_view.objects.filter( product_id = prod_id,
			product_type_id = prod_type).first()
	
	'''  OPEN FILE FROM A Internet URL '''
	env = settings.EXEC_ENV
	if env == 'DEV' or env == 'TESTING':
		if prod_type == 'STOCK-IMAGE' and prod_img.publisher != 'ARTEVENUE':
			response = requests.get(prod_img.url)
			img_source = Image.open(BytesIO(response.content))
		else :
			img_source = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + prod_img.url)
	else:
		img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)			
	
	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = m_id, image_type = "APPLY").values(
				'url', 'moulding__width_inner_inches', 'border_slice').first()
	
	if moulding:
	
		m_width_inch = float(moulding['moulding__width_inner_inches'])
		
		# Image width displayed in browser in inches
		disp_inch = 450//96
		
		ratio = disp_inch / user_width
		
		border = int(m_width_inch * ratio* 96)		
		#border = int(m_width_inch * 96/ user_width)
		
		m_size = int(mount_size * 96 * ratio)
		#m_size = int(mount_size * 960 / user_width)
		
		if m_size > 0 and mount_color != '' and mount_color != '0' and mount_color != 'None':

			img_with_mount = addMount(img_source, mount_color, m_size, m_size, m_size, m_size)
			
			framed_img = applyFrame( img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
		else:
			framed_img = applyFrame( img_source, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
	else :
		# No moulding, returing the image as it is.
		framed_img = Image.new("RGB", (img_source.width, img_source.height), 0)
		framed_img.paste(img_source, (0,0))

	##framed_img = dropShadow(framed_img, shadow=(0x00,0x00,0x00,0xff))
	
	framed_img.show()
	
	return framed_img
	
def applyFrame(img_source, ref_url, border_top, border_right, border_bottom, border_left, slice_top, slice_right, slice_bottom, slice_left):
	# Get the image from the server to extract the frame border
	from django.conf import settings
	path = settings.MOULDING_ROOT + ref_url

	img_source = dropInnerShadow(img_source)

	mld_img = Image.open(path)

	box_topleftcorner = (0, 0, slice_left, slice_top)

	topleftcorner = mld_img.crop(box_topleftcorner)
	topleftcorner = topleftcorner.resize((border_left, border_top))
	
	box_topedge = (slice_left, 0, mld_img.width - slice_right, slice_top)
	topedge = mld_img.crop(box_topedge)
	topedge = topedge.resize((topedge.width, border_top))
	
	box_toprightcorner = (mld_img.width - slice_right, 0, mld_img.width, slice_top)
	toprightcorner = mld_img.crop(box_toprightcorner)
	toprightcorner = toprightcorner.resize((border_right, border_top))

	box_rightedge = (mld_img.width - slice_right, slice_top, mld_img.width, mld_img.height - slice_bottom)
	rightedge = mld_img.crop(box_rightedge)
	rightedge = rightedge.resize((border_right, rightedge.height))
	
	box_bottomrightcorner = (mld_img.width - slice_right, mld_img.height - slice_bottom, mld_img.width, mld_img.height)
	bottomrightcorner = mld_img.crop(box_bottomrightcorner)
	bottomrightcorner = bottomrightcorner.resize((border_right, border_bottom))
	

	box_bottomedge = (slice_left, mld_img.height - slice_bottom, mld_img.width - slice_right, mld_img.height)
	bottomedge = mld_img.crop(box_bottomedge)
	bottomedge = bottomedge.resize((bottomedge.width, border_bottom))
	
	box_bottomleftcorner = (0, mld_img.height - slice_bottom, slice_left, mld_img.height)
	bottomleftcorner = mld_img.crop(box_bottomleftcorner)
	bottomleftcorner = bottomleftcorner.resize((border_left, border_bottom))

	box_leftedge = (0, slice_top, slice_left, mld_img.height - slice_bottom)
	leftedge = mld_img.crop(box_leftedge)
	leftedge = leftedge.resize((border_left, leftedge.height))
	# drop shadow for left edge
	#leftedge = dropShadow(leftedge, shadow=(0x00,0x00,0x00,0xff))
	#leftedge = dropFrameShadowIn(leftedge)
	
	new_img = Image.new("RGB", (img_source.width + border_left + border_right, img_source.height + border_top + border_bottom), 0)

	new_img.paste(img_source, (border_left,border_top)) 	# paste the image to apply the border to
	
	'''***************
	Repeat border for the TOP EDGE
	'''
	width_to_fill = int(new_img.width - (border_left + border_right))  # corners are already placed
	num_of_imgs = width_to_fill // topedge.width # number of images that will fit in the edge
	remainder = width_to_fill % topedge.width # the remainder part

	curr_coord = int(border_left)
	for l in range( curr_coord, width_to_fill, topedge.width):
		new_img.paste(topedge, (l, 0))

	# paste remainder, if any
	if remainder > 0:
		top_rem = topedge.crop( (topedge.width - remainder, 0, topedge.width, topedge.height) )
		new_img.paste( top_rem, ((width_to_fill + border_left - remainder), 0))	

	'''***************
	Repeat border for the BOTTOM EDGE
	'''
	width_to_fill = int(new_img.width - (border_left + border_right))  # corners are already placed
	num_of_imgs = width_to_fill // bottomedge.width # number of images that will fit in the edge
	remainder = width_to_fill % bottomedge.width # the remainder part

	curr_coord = int(border_left)
	for l in range( curr_coord, width_to_fill, bottomedge.width):
		new_img.paste(bottomedge, (l, new_img.height - border_bottom))


	# paste remainder, if any
	if remainder > 0:
		bottom_rem = bottomedge.crop( (bottomedge.width - remainder, 0, topedge.width, bottomedge.height) )
		new_img.paste( bottom_rem, ((width_to_fill + border_left - remainder), new_img.height - border_bottom))

	'''***************
	Repeat border for the LEFT EDGE
	'''
	height_to_fill = int(new_img.height - (border_top + border_bottom))  # corners are already placed
	num_of_imgs = height_to_fill // leftedge.height # number of images that will fit in the edge
	
	curr_coord = int(border_top)
	if leftedge.height >= height_to_fill:
		leftedge = leftedge.crop( (0, 0, leftedge.width, height_to_fill) )
		
	remainder = height_to_fill % leftedge.height # the remainder part

	for l in range( curr_coord, height_to_fill, leftedge.height):
		new_img.paste(leftedge, (0, l))

	# paste remainder, if any
	if remainder > 0:
		left_rem = leftedge.crop( (0, 0, leftedge.width, remainder) )
		new_img.paste( left_rem, (0, (height_to_fill + border_bottom - remainder)) )
	
	'''***************
	Repeat border for the RIGHT EDGE
	'''
	height_to_fill = int(new_img.height - (border_top + border_bottom))  # corners are already placed
	num_of_imgs = height_to_fill // rightedge.height # number of images that will fit in the edge
	remainder = height_to_fill % rightedge.height # the remainder part

	curr_coord = int(border_top)
	for l in range( curr_coord, height_to_fill, rightedge.height):
		new_img.paste(rightedge, (new_img.width - border_right, l))

	
	# paste remainder, if any
	if remainder > 0:
		right_rem = rightedge.crop( (0, rightedge.height - remainder, rightedge.width, rightedge.height) )
		new_img.paste( right_rem, ( new_img.width - border_right, height_to_fill + border_bottom - remainder) )
	

	new_img.paste(topleftcorner, (0,0))
	#new_img.paste(topedge, (border_left,0))
	new_img.paste(toprightcorner, (new_img.width - border_right, 0))
	#new_img.paste(rightedge, (new_img.width - border_right, border_top))
	new_img.paste(bottomrightcorner, (new_img.width - border_right, new_img.height - border_bottom))
	#new_img.paste(bottomedge, (border_left, new_img.height - border_bottom) )
	new_img.paste(bottomleftcorner, (0, new_img.height - border_bottom))
	#new_img.paste(leftedge, (0, border_top))

	#new_img = dropShadow(new_img, shadow=(0x00,0x00,0x00,0xff))
	
	return new_img
	
	
def dropInnerShadow( img, gradient_magnitude=50.0 ):
	shadow_color = 0xADADAD		
	img = img.convert('RGBA')
	width, height = img.size
	gradient = Image.new('L', (1, height), color=0xFF)	
	for y in range(height):
		gradient.putpixel((0, y), int(255 * (1 - gradient_magnitude * float(y)/height)))
		#gradient.putpixel((0, y), 255-y)
		
	alpha = gradient.resize(img.size)
	black_im = Image.new('RGBA', (width, height), color=shadow_color)
	black_im.putalpha(alpha)
	gradient_im = Image.alpha_composite(img, black_im)


	gradient = Image.new('L', (width, 1), color=0xFF)	
	for x in range(width):
		#gradient.putpixel((0, y), 255-y)
		gradient.putpixel((x, 0), int(255 * (1 - gradient_magnitude * float(x)/width)))
	alpha = gradient.resize(gradient_im.size)
	black_im = Image.new('RGBA', (width, height), color=shadow_color)
	black_im.putalpha(alpha)
	gradient_im = Image.alpha_composite(gradient_im, black_im)


	'''
	gradient_magnitude = 75.0
	gradient = Image.new('L', (1, height), color=0xFF)
	for y in range(height):
		gradient.putpixel((0, y), int(255 * (1 - gradient_magnitude * float(y)/height)))
		#gradient.putpixel((0, y), 255-y)
	alpha = gradient.resize(gradient_im.size)
	alpha = alpha.transpose(Image.FLIP_TOP_BOTTOM)
	black_im = Image.new('RGBA', (width, height), color=0x5F5F5F)
	black_im.putalpha(alpha)
	gradient_im = Image.alpha_composite(gradient_im, black_im)


	gradient = Image.new('L', (width, 1), color=0xFF)	
	for x in range(width):
		#gradient.putpixel((0, y), 255-y)
		gradient.putpixel((x, 0), int(255 * (1 - gradient_magnitude * float(x)/width)))
	alpha = gradient.resize(gradient_im.size)
	alpha = alpha.transpose(Image.FLIP_LEFT_RIGHT)
	black_im = Image.new('RGBA', (width, height), color=0x5F5F5F)
	black_im.putalpha(alpha)
	gradient_im = Image.alpha_composite(gradient_im, black_im)
	'''
	
	return gradient_im
	

def dropMountShadow( img_source ):
	##### Create mount shaddow effect.
	
	w = img_source.width
	h = img_source.height
	
	#TOP 3 lines
	line_w_dark = Image.new(img_source.mode, (w, 1), 0x4E4E4E)
	img_source.paste(line_w_dark, [0, 0, w, 1] )
	img_source.paste(line_w_dark, [0, 1, w, 2] )		
	img_source.paste(line_w_dark, [0, 2, w, 3] )		
	img_source.paste(line_w_dark, [0, 3, w, 4] )		

	#LEFT 4 lines
	line_h_dark = Image.new(img_source.mode, (1, h), 0x4E4E4E)
	img_source.paste(line_h_dark, [0, 0, 1, h] )		
	img_source.paste(line_h_dark, [1, 0, 2, h] )		
	img_source.paste(line_h_dark, [2, 0, 3, h] )		
	img_source.paste(line_h_dark, [3, 0, 4, h] )		


	line_w_light = Image.new(img_source.mode, (w, 1), 0xEDEDED)
	line_h_light = Image.new(img_source.mode, (1, h), 0xEDEDED)

	#BOTTOM 4 lines
	img_source.paste(line_w_light, [0, h-1, w, h])
	line_w_light_1 = Image.new(img_source.mode, (w-2, 1), 0xBEBEBE)
	img_source.paste(line_w_light_1, [1, h-2, w-1, h-1])
	line_w_light_2 = Image.new(img_source.mode, (w-4, 1), 0xF1F1F1)
	img_source.paste(line_w_light_2, [2, h-3, w-2, h-2])
	img_source.paste(line_w_light_2, [2, h-4, w-2, h-3])
	line_w_light_3 = Image.new(img_source.mode, (w-6, 1), 0xF1F1F1)
	img_source.paste(line_w_light_3, [3, h-5, w-3, h-4])


	#RIGHT 4 line
	img_source.paste(line_h_light, [w-1, 0, w, h] )
	line_h_light_1 = Image.new(img_source.mode, (1, h-2), 0xBEBEBE)
	img_source.paste(line_h_light_1, [w-2, 1, w-1, h-1] )
	line_h_light_2 = Image.new(img_source.mode, (1, h-4), 0xF1F1F1)	
	img_source.paste(line_h_light_2, [w-3, 2, w-2, h-2] )
	img_source.paste(line_h_light_2, [w-4, 2, w-3, h-2] )
	line_h_light_3 = Image.new(img_source.mode, (1, h-6), 0xF1F1F1)	
	img_source.paste(line_h_light_3, [w-5, 3, w-4, h-3] )

	return img_source
	

def stretchedCanvas( img_source ):
	w = img_source.width
	h = img_source.height
	
	#############################
	### create right side edge
	#############################
	# get 10 pixel from right edge of the image
	r_10 = img_source.crop([w - 10, 0, w, h])
	r_image = Image.new(img_source.mode,  (10, h + 10), (255, 0, 0, 0) )
	for i in range(9):
		r_line_img = r_10.crop([i,0, i+1, r_10.height])
		r_image.paste( r_line_img, (i,i) )


	#############################
	### create bottom edge
	#############################
	# get 10 pixel from bottom edge of the image
	b_10 = img_source.crop([0, h - 10, w, h])
	b_image = Image.new(img_source.mode,  (w + 10, 10), (255, 0, 0, 0) )
	for i in range(9):
		b_line_img = b_10.crop([0,i, b_10.width, i + 1])
		b_image.paste( b_line_img, (i,i) )

	stretchedImg = Image.new(img_source.mode,  (w + 10, h + 10), (255, 0, 0, 0) )
	stretchedImg.paste( img_source, (0, 0) )

	line_w_light = Image.new(img_source.mode, (w, 1), 0xBEBEBE)
	line_h_light = Image.new(img_source.mode, (1, h), 0xBEBEBE)
	stretchedImg.paste( line_w_light, (1, h) )
	stretchedImg.paste( line_h_light, (w, 1) )
	
	stretchedImg.paste( r_image, (w+1, 0) )
	stretchedImg.paste( b_image, (0, h+1) )
	stretchedImg.show()

	return r_image
		

'''	
def tilt_image(img, border_width=None, flag=False):
	from PIL import Image, ImageEnhance, ImageFilter
	import numpy as np
	import math
	import cv2        

	def find_coeffs(source_coords, target_coords):
		matrix = []

		for s, t in zip(source_coords, target_coords):
			matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
			matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])

		A = np.matrix(matrix, dtype=np.float)
		B = np.array(source_coords).reshape(8)
		X = np.dot(numpy.linalg.inv(A.T * A) * A.T, B)

		return np.array(X).reshape(8)

	img = np.array(img) 
	img = img[:, :, ::-1].copy() 

	width = img.shape[1]
	height = img.shape[0]

	theta = 10
	s = width/height
	if s >= 2:
		theta = 20
	elif s <= 0.5:
		theta = 1

	r = 0.5*(1-1/(1+1/s*math.tan(theta*math.pi/180)))
	R = 0.5*(1+1/(1+1/s*math.tan(theta*math.pi/180)))

	new_height = [height*r, (R*height)]
	new_width = width*math.cos(theta*math.pi/180)

	inp_coordinates = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
	output_coordinates = np.float32([[0, 0], [new_width, new_height[0]], [new_width, new_height[1]], [0, height]])

	matrix = cv2.getPerspectiveTransform(inp_coordinates,output_coordinates)

	imgOutput = cv2.warpPerspective(img, matrix, (width,height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=[255,255,255,0])

	imgOutput = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2RGB)
	img = Image.fromarray(imgOutput)

	#Creating image border
	if not border_width:
		border_width = 40
	img_border = img.crop((0, 0, border_width, height))

	border_imgOutput = img_border
	width1, height1 = img_border.size

	theta1 = theta/6

	if s>1:
		theta1 = theta/3
		
	r1 = 0.5*(1-1/(1+1/s*math.tan(theta1*math.pi/180)))
	R1 = 0.5*(1+1/(1+1/s*math.tan(theta1*math.pi/180)))

	new_height1 = [height1*r1, (R1*height1)]
	new_width1 = width1*math.cos(theta1*math.pi/360)
	img_border = np.array(img_border) 
	img_border = img_border[:, :, ::-1].copy() 

	border_inp = np.float32([[0, 0], [width1, 0], [width1, height1], [0, height1]])
	border_out = np.float32([[0, 0], [new_width1, new_height1[0]], [new_width1, new_height1[1]], [0, height1]])

	border_matrix = cv2.getPerspectiveTransform(border_inp,border_out)
	img_border = cv2.warpPerspective(img_border, border_matrix, (width1,height1), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=[255,255,255,0])

	#Creating mirror image of border
	img_border = cv2.flip(img_border, 1)       
	img_border = cv2.cvtColor(img_border, cv2.COLOR_BGRA2RGB)
	img_border = Image.fromarray(img_border) 

	#Darkening image
	enhancer = ImageEnhance.Brightness(img_border)
	img_border = enhancer.enhance(0.7)

	img_border = np.array(img_border) 
	img_border = img_border[:, :, ::-1].copy() 
	img_border = cv2.cvtColor(img_border, cv2.COLOR_BGRA2RGB)


	for i in range(len(img_border)):
		for j in range(border_width):
			if (img_border[i][j][0] == 178):
				img_border[i][j] = [255, 255, 255]
		if (not flag):
			for k in range(int(border_width/2)):
				if (img_border[i][k] != 255).all():
					img_border[i][k] = [236,236,210]
					if k == 0:
						img_border[i][k] = [173, 173, 173]
	if not flag:
		for i in range(width1):
			check = 0
			for j in range(height1):
				if (img_border[j][i][2] != 255) and check !=1:
					img_border[j][i] = [173, 173, 173]
					check = check + 1
					
		for i in range(width1):
			check = 0
			j = height1 - 1
			while(j > height1/2):
				if (img_border[j][i][2] != 255) and check !=1:
					img_border[j][i] = [173, 173, 173]
					check = check + 1
				j = j-1


	img_border = cv2.GaussianBlur(img_border, (5,5), 1)
	#Merging border and tilted image
	image = cv2.hconcat([img_border, imgOutput])

	#Improving resolution
	#sr = cv2.dnn_superres.DnnSuperResImpl_create()

	# path = "FSRCNN_x2.pb"
	# sr.readModel(path)
	# sr.setModel("fsrcnn",2)
	# result = sr.upsample(image)  
	# result = cv2.resize(image,(width, height), interpolation = cv2.INTER_NEAREST)
	result = image
	image = Image.fromarray(result)

	return image

'''


def tilt_image(img, border_width=None, frame_flag=True, frame_depth=None, white_frame=False):
   # frame_flag: TRUE - Left border from the image
   # frame_flag: FALSE - Left border half grey and half from the image

	from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
	import numpy as np
	import math
	import cv2

	width = img.size[0]
	height = img.size[1]


	img_copy = img

	img = np.array(img) 
	img = img[:, :, ::-1].copy()

	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	img= Image.fromarray(img)

	if not frame_flag:
		width = width + 2
		height = height + 4
		mask = Image.new('RGB', (width, height), (173,173,173,0))
		mask = np.array(mask) 
		mask = mask[:, :, ::-1].copy()
		mask = cv2.GaussianBlur(mask, (7,7), 550)
		mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)
		mask = Image.fromarray(mask)
		mask.paste(img, (0,2))
		img = mask

	img = np.array(img) 
	img = img[:, :, ::-1].copy() 
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

	theta = 10
	s = width/height
	if s >= 2:
	   theta = 35
	elif s <= 0.5:
	   theta = 20
	f =2000

	h1 = height/2 - f*(height/2)/(f+width*np.sin(theta*math.pi/180))
	H1 = height/2 + f*(height/2)/(f+width*np.sin(theta*math.pi/180))

	x = 1 #Artificial variable
	new_width = f*width/(f+width*np.sin(theta*math.pi/180))*np.cos(theta*math.pi/180)*x

	inp_coordinates = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
	output_coordinates = np.float32([[0, 0], [new_width, h1], [new_width, H1], [0, height]])

	matrix = cv2.getPerspectiveTransform(inp_coordinates,output_coordinates)

	img = cv2.warpPerspective(img, matrix, (width,height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=[255,255,255,0])

	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	#img = Image.fromarray(imgOutput)

   #Creating image border
	if not border_width:
		border_width = 30

	if frame_depth:
		#if frame_depth > border_width:
		#	diff = frame_depth - border_width
		img_border = img_copy.crop((0, 0, border_width, img_copy.height))
		img_border = img_border.resize((frame_depth, img_border.height))
		border_width = frame_depth	
	else:
		img_border = img_copy.crop((0, 0, border_width, img_copy.height))
	

	#img_border = img_copy.crop((0, 0, border_width, img_copy.height))
	border_height = img_border.height

	if not frame_flag:
		border_height = img_border.height + 4
		border_width = border_width + 2
		mask = Image.new('RGB', (border_width, border_height), (236,236,226,0))
		mask.paste(img_border, (0,2))
		img_border = mask

	img_border = np.array(img_border) 
	img_border = img_border[:, :, ::-1].copy() 
	img_border = cv2.cvtColor(img_border, cv2.COLOR_BGR2RGB)

	slope = -0.3

	border_height1 = [slope*border_width + height, -border_width*slope]
	img_border = np.array(img_border) 
	img_border = img_border[:, :, ::-1].copy() 

	border_inp = np.float32([[0, 0], [border_width, 0], [border_width, border_height], [0, border_height]])
	border_out = np.float32([[0, 0], [border_width, border_height1[1]], [border_width, border_height1[0]], [0, border_height]])

	border_matrix = cv2.getPerspectiveTransform(border_inp,border_out)
	img_border = cv2.warpPerspective(img_border, border_matrix, (border_width,border_height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=[255,255,255,0])

	#Creating mirror image of border
	img_border = cv2.flip(img_border, 1)       
	img_border = cv2.cvtColor(img_border, cv2.COLOR_BGRA2RGB)
	img_border = Image.fromarray(img_border) 

	#Darkening image
	enhancer = ImageEnhance.Brightness(img_border)

	if white_frame:
		img_border = enhancer.enhance(0.9)
	else:
		img_border = enhancer.enhance(0.7)

	img_border = np.array(img_border) 
	img_border = img_border[:, :, ::-1].copy() 
	img_border = cv2.cvtColor(img_border, cv2.COLOR_BGRA2RGB)

	for i in range(border_height):
		for j in range(border_width):
			if (i < border_height - border_height1[0] + slope*j):
							img_border[i][j] = [255, 255, 255]
			if (i > border_height1[0] - slope*j):
							img_border[i][j] = [255, 255, 255]
					
		if (not frame_flag):
			for k in range(int(border_width/2)):
				if (i > border_height - border_height1[0] + slope*k+2) and (i < border_height1[0] - slope*k-2) and k>1:
					img_border[i][k] = [236,236,226]
	  
	img_border = cv2.GaussianBlur(img_border, (3,3), 1)

	img_border = cv2.cvtColor(img_border, cv2.COLOR_BGRA2RGB)

	#Merging border and tilted image
	image = cv2.hconcat([img_border, img])

	image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

	image = Image.fromarray(image)

	# Add left edge gradient 
	if frame_flag and not white_frame:
		line = Image.new('L', (1, height))    
		line = np.array(line) 
		line = line[:, ::-1].copy()
		p = 255
		for i in range(height):
					 line[i] = (4*p/height)*(-i**2/height + i)

		line = cv2.GaussianBlur(line, (5,5), 3)
		line = Image.fromarray(line)

		image.paste(line, (border_width, 0))


	return image

	
	
def img_polygon_crop(img):

	xy = [(0,10), (10, 0), (10, im.height), (0, im.height-10)]
	mask = Image.new("L", im.size, 0)
	draw = ImageDraw.Draw(mask)
	draw.polygon(xy, fill=255, outline=None)
	black = Image.new("L", im.size, 0)
	result = Image.composite(im, black, mask)
	
	return result


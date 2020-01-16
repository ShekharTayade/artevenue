from artevenue.models import Stock_image, Moulding_image, User_image, Product_view
from django.contrib.auth.models import User
from django.conf import settings

from django.http import HttpResponse
from decimal import Decimal

from PIL import Image, ImageFilter

import requests
from io import BytesIO

import base64
from io import StringIO


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
		if prod_type == 'STOCK-IMAGE':
			response = requests.get(prod_img.url)
			img_source = Image.open(BytesIO(response.content))
		else :
			img_source = Image.open(settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + prod_img.url)
	else:
		img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)			
	
	
	#else :
	#	response = requests.get(prod_img.url)
	#	img_source = Image.open(BytesIO(response.content))

	
	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = m_id, image_type = "APPLY").values(
				'url', 'moulding__width_inches', 'border_slice').first()
	
	if moulding:
	
		m_width_inch = float(moulding['moulding__width_inches'])
		
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
							float(moulding['border_slice']), float(moulding['border_slice']) )
		else:
			framed_img = applyBorder( request, img_source, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
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
	
	

def addMount( img_source, mount_color, border_top, border_right, border_bottom, border_left):

	img = Image.new( "RGB", (img_source.width + border_left + border_right, img_source.height + border_top + border_bottom), mount_color)  

	img.paste(img_source, (border_left, border_top))
	
	return img

def applyBorder(request, img_source, ref_url, border_top, border_right, border_bottom, border_left, slice_top, slice_right, slice_bottom, slice_left):

	# Get the image from the server to extract the frame border
	from django.conf import settings
	path = settings.MOULDING_ROOT + ref_url	
	
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
	#leftedge = dropInnerShadow(leftedge)
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
	#response = requests.get("http://www.podexchange.com/dsi/lowres/11/11_PSMLT-166_lowres.jpg")
	#if prod_img.publisher == '1001':
	img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + prod_img.url)			
	#else:
	#	response = requests.get(prod_img.url)
	#	img_source = Image.open(BytesIO(response.content))
	
	# Get all mouldings
	moulding = Moulding_image.objects.filter(image_type = "APPLY").values(
				'url', 'moulding__width_inches', 'border_slice')
	

	# Image width displayed in browser in inches
	disp_inch = 150//96
	
	ratio = disp_inch / user_width
	
	frames_array = []
	
	import traceback
	try:
		for m in moulding:
			m_width_inch = float(m['moulding__width_inches'])
			border = int(m_width_inch * ratio * 96)

			framed_img = applyBorder( request, img_source, m['url'], border, border, border, border,
							float(m['border_slice']), float(m['border_slice']), 
							float(m['border_slice']), float(m['border_slice']) )

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
				'url', 'moulding__width_inches', 'border_slice').first()
	
	if moulding:
	
		m_width_inch = float(moulding['moulding__width_inches'])
		
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
							float(moulding['border_slice']), float(moulding['border_slice']) )
		else:
			framed_img = applyBorder( request, img_to_frame, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
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
				'url', 'moulding__width_inches', 'border_slice').first()
	
	if moulding:
	
		m_width_inch = float(moulding['moulding__width_inches'])
		
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
							float(moulding['border_slice']), float(moulding['border_slice']) )
		else:
			framed_img = applyBorder( request, img_to_frame, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
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


	
def dropShadow( image, offset=(8,8), background=0xffffff, shadow=0x444444, 
                border=10, iterations=3):
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
	back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], 
	shadowTop + image.size[1]] )
  
	# Apply the filter to blur the edges of the shadow.  Since a small kernel
	# is used, the filter must be applied repeatedly to get a decent blur.
	n = 0
	while n < iterations:
		back = back.filter(ImageFilter.BLUR)
		n += 1
    
	# Paste the input image onto the shadow backdrop  
	imageLeft = border - min(offset[0], 0)
	imageTop = border - min(offset[1], 0)
	back.paste(image, (imageLeft, imageTop))

	return back
  
  
def dropInnerShadow(image, offset=(2,2), background=0x666666, shadow=0x444444, 
                border=3, iterations=3):
				
	# Create the backdrop image -- a box in the background colour with a 
	# shadow on it.
	totalWidth = image.size[0] + abs(offset[0]) + border
	totalHeight = image.size[1]
	back = Image.new(image.mode, (totalWidth, totalHeight), background)

	# Place the shadow, taking into account the offset from the image
	shadowLeft = border + max(offset[0], 0)
	shadowTop = 0   ##border + max(0, 0)
	back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], 
	shadowTop + image.size[1]] )
  
	# Apply the filter to blur the edges of the shadow.  Since a small kernel
	# is used, the filter must be applied repeatedly to get a decent blur.
	n = 0
	while n < iterations:
		back = back.filter(ImageFilter.BLUR)
		n += 1
    
	# Paste the input image onto the shadow backdrop  
	imageLeft = border - offset[0]
	imageTop = border - offset[1]
	back.paste(image, (0, 0))

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
	
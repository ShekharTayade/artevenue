from django import template
from decimal import Decimal

from artevenue.models import Moulding, Collage_stock_image

from artevenue.views  import price_views

register = template.Library()

@register.filter
def add_width_frame_mount(a, b):

	# Used for adding size of frame and mount to total size
	# size of mount and frame to be added to top and and bottom
	# and left and right side, hence, multiplied by 2
	if not a:
		return 0
	if b:
		return a+b
	else:
		return a
		
@register.filter
def add_width(a, b):

	if not a:
		return 0
	if b:
		return a+b
	else:
		return a

		
@register.filter
def multiply(a,b):
	return a * b

@register.filter
def divide(a,b):
	return a / b


@register.simple_tag
def get_price(width, aspect_ratio, sqin_price, user_width):
	if user_width > 0:
		width = user_width
	else:
		if width > 10:
			width = 10
	height = round(width / aspect_ratio)

	# Small size prices increased by 20%  -- 26 Sep 2020
	size = width * height
	if size <= 100:
		sqin_price = sqin_price + (sqin_price * 20/100)
	elif size <= 256:
		sqin_price = sqin_price + (sqin_price * 15/100)
	elif size <= 500:
		sqin_price = sqin_price + (sqin_price * 10/100)
	
	return Decimal(round( float(width * height * sqin_price ) , -1))

@register.filter
def filter_by_cart_id(qs, cart_id):
    return qs.filter(cart_id=cart_id)

'''	
@register.filter	
def get_price(a, aspect_ratio):
	width = 16 
	height = 16 / aspect_ratio
			
	return round(a * width * height, -1)
'''

@register.filter	
def get_mountcolor(cnt):

	'''
	remainder = cnt % 5
	if remainder == 0:
		color = 'none'
	if remainder == 1:
		color = '#ffffff'
	if remainder == 2:
		color = '#fffdd0'
	if remainder == 2:
		color = '#fffff0'
	if remainder == 3:
		color = '#000000'
	if remainder == 4:
		color = '#800000'
	'''
	color = '#fffff0'
	
	return color

@register.filter	
def indian_number_format(input):
	'''
	import locale
	locale.setlocale(locale.LC_MONETARY, 'en_IN')
	return locale.currency(input, grouping=True)
	'''

	from babel.numbers import format_currency
	return format_currency(input, 'INR', locale='en_IN')
	
	
@register.filter
def get_height(width, aspect_ratio):
	height = round(width / aspect_ratio)
	
	return height


@register.filter
def get_dict_item(dictionary, key):
    return dictionary.get(key)
	
	
@register.filter
def get_frame_name_innerwidth(frame_id, nameorwidth):
	if frame_id == '':
		return ''
	try:
		m = Moulding.objects.get(pk=frame_id)
		name = m.name
		inner_width = m.width_inner_inches
	except Moulding.DoesNotExist:
		name = ''
		inner_width = 0
	if nameorwidth == 'NAME':
		return name
	else:
		return inner_width

@register.filter
def replace(str, args):
	old, new = args.split(',')
	if str:
		return str.replace(old, new)
	else:
		return ''

@register.simple_tag
def get_collage_price( collage_id, aspect_ratio, user_width ):

	if user_width > 0:
		width = user_width
	else:
		if width >= 10:
			width = 10
	height = round(width / aspect_ratio)

	prods = Collage_stock_image.objects.filter(collage_id = collage_id,
		stock_collage__is_published = True)
	
	p_arr = []
	t_price = 0
	for p in prods:
		price = price_views.get_prod_price(p.stock_image_id, 
				prod_type='STOCK-IMAGE',
				image_width=width, 
				image_height=height,
				print_medium_id = 'PAPER',
				acrylic_id = '1',
				moulding_id = 18,
				mount_size = 1,
				mount_id = 3,
				board_id = 1,
				stretch_id = '')
			
		#p_arr.append( price['item_price'] )
		t_price = t_price + price['item_price']
		print(str(t_price))
	#for price in p_arr:
	#	t_price = t_price + price
	return Decimal(t_price)

@register.filter
def replace_comma(str):
   return str.replace(',', '_')
   
@register.filter
def replace_dash(str):
   return str.replace('-', ' ')

@register.filter
def endswith(value, suffix):
    return value.endswith(suffix)   
	
@register.filter
def startswith(value, prefix):
    return value.startswith(prefix)   

@register.filter
def contains(value, str):
	if value.find(str) >= 0:
		ret = True
	else:
		ret = False
		
	return ret 

@register.filter
def convert_to_k(value):
	if int(value) > 0:
		if int(value) <= 999:
			ret = str(value)
		else:
			ret = str(round((int(value) / 1000))) + "k"
	else:
		ret = value
	return ret
	
@register.filter
def create_cat_filenm(val=None, disp=None):
	nm = val
	if disp == 150:
		print(150)
		nm = "img/all_category_images/150/" + val.lower() + "_150.jpg"
	elif disp == 75:
		print(75)
		nm = "img/all_category_images/75/" + val.lower() + "_75.jpg"
	else :
		nm = None
		
	return nm
	
@register.filter
def get_art_price_without_tax(val=None):
	unit_price = round( float(val)/ (1 + (12/100)), 2 )
	return Decimal(unit_price)
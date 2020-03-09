from django import template
from decimal import Decimal

from artevenue.models import Moulding

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

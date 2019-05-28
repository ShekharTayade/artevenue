from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def add_width_frame_mount(a, b):

	# Used for adding size of frame and mount to total size
	# size of mount and frame to be added to top and and bottom
	# and left and right side, hence, multiplied by 2
	if not a:
		return 0
	if b:
		return (a*2)+(b*2)
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

@register.simple_tag
def get_price(width, aspect_ratio, sqin_price):
	if width > 16:
		width = 16
	height = round(width / aspect_ratio)
	
	return Decimal(round( float(width * height * sqin_price ) , -1))

'''	
@register.filter	
def get_price(a, aspect_ratio):
	width = 16 
	height = 16 / aspect_ratio
			
	return round(a * width * height, -1)
'''

@register.filter	
def get_mountcolor(cnt):

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
		
	return color
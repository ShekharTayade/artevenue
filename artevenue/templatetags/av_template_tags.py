from django import template
register = template.Library()

@register.simple_tag
def create_cat_filenm(val=None):
	nm = val
	nm = "img/all_category_images/150" + val + "_150.jpg"
	'''
	if disp == '150':
		nm = "img/all_category_images/150" + val + "_150.jpg"
	elif disp == '75':
		nm = "img/all_category_images/75" + val + "_75.jpg"
	'''
	return nm
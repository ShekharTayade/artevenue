from django import template
from decimal import Decimal

from gallerywalls.models import Gallery_variation, Gallery_item
from artevenue.models import Stock_image
from artevenue.views  import price_views
from gallerywalls.views import get_variation_item_price

register = template.Library()

@register.filter
def get_gallery_parent_price(gallery_id):

	gallery_variation = Gallery_variation.objects.filter(gallery_id = gallery_id, is_parent = True).first()
	
	gallery_items = Gallery_item.objects.filter(gallery_id = gallery_id, 
		gallery_variation = gallery_variation)
			
	gallery_items = gallery_items.values(
			'item_id', 'gallery_id', 'gallery_variation_id', 'product_id', 'product_name', 'product_type_id',
			'moulding_id', 'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id',
			'mount__name', 'mount__color', 'mount_size', 'board_id', 'acrylic_id', 'stretch_id', 'image_width', 
			'image_height', 'moulding__width_inner_inches')

	gallery_variation_price = 0	
	for gal_item in gallery_items:
		#prod = Stock_image.objects.filter(product_id = gal_item['product_id']).first()
		#if prod:
		item_price = get_variation_item_price(gal_item['item_id'])
		gallery_variation_price = gallery_variation_price + item_price
		#else:
		#	gallery_variation_price = 0

	return gallery_variation_price
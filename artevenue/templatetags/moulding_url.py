from artevenue.models import Moulding_image
from django import template
from django.conf import settings
	
register = template.Library()

@register.simple_tag
def moulding_url(moulding_id):

	if moulding_id :
		# Get moulding
		moulding = Moulding_image.objects.filter(moulding_id = moulding_id, image_type = "APPLY").values(
					'url', 'moulding__width_inches', 'border_slice').first()
		
		path = settings.MOULDING_ROOT + moulding['url']
	else :
		path = settings.MOULDING_ROOT
	
	return path
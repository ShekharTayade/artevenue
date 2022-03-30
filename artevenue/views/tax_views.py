
from datetime import datetime
import datetime
from django.conf import settings

from artevenue.models import Tax

today = datetime.date.today()


def get_taxes():

	stock_image_tax_rate = 0
	user_image_tax_rate = 0
	stock_collage_tax_rate = 0
	original_art_tax_rate = 0
	frame_tax_rate = 0
	mount_tax_rate = 0
	acrylic_tax_rate = 0
	board_tax_rate = 0
	stretch_tax_rate = 0
	oth_tax_rate = 0

	taxes = Tax.objects.filter(effective_from__lte = today, effective_to__gte = today,
		store_id = settings.STORE_ID)
	
	## Currently all components, except the image, carry the same tax rate. hence using 
	## 'oth_tax_rate', which basically means all other components except image.
	for t in taxes:
		if t.name == 'STOCK-IMAGE':
			stock_image_tax_rate = t.tax_rate
		if t.name == 'USER-IMAGE':
			user_image_tax_rate = t.tax_rate
		if t.name == 'STOCK-COLLAGE':
			stock_collage_tax_rate = t.tax_rate
		if t.name == 'ORIGINAL-ART':
			original_art_tax_rate = t.tax_rate
		if t.name == 'FRAME':
			frame_tax_rate = t.tax_rate
			oth_tax_rate = t.tax_rate
		if t.name == 'MOUNT':
			mount_tax_rate = t.tax_rate
			oth_tax_rate = t.tax_rate
		if t.name == 'ACRYLIC':
			acrylic_tax_rate = t.tax_rate
			oth_tax_rate = t.tax_rate
		if t.name == 'BOARD':
			board_tax_rate = t.tax_rate
			oth_tax_rate = t.tax_rate
		if t.name == 'STRETCH':
			stretch_tax_rate = t.tax_rate
			oth_tax_rate = t.tax_rate			
		if t.name == 'NON-RECTANGULAR':
			non_rectangular_tax_rate = t.tax_rate
			oth_tax_rate = t.tax_rate
            

	return ( {'stock_image_tax_rate':stock_image_tax_rate, 'user_image_tax_rate':user_image_tax_rate,
		'stock_collage_tax_rate':stock_collage_tax_rate, 'original_art_tax_rate':original_art_tax_rate, 
		'frame_tax_rate':frame_tax_rate, 'mount_tax_rate':mount_tax_rate, 
		'acrylic_tax_rate':acrylic_tax_rate, 'board_tax_rate':board_tax_rate, 
		'stretch_tax_rate':stretch_tax_rate, 'oth_tax_rate':oth_tax_rate, 'non_rectangular_tax_rate': non_rectangular_tax_rate} )
		
		
from django.db import models
from artevenue.models import Stock_image, Stock_image_category, Product_type, Product_view, Print_medium, Moulding
from artevenue.models import Mount, Board, Acrylic, Stretch, Cart_item, Order_items


IMG_TYPE  = (
		('LS', 'LIFE STYLE'),
		('PR', 'PRODUCT'),
		('3D', '3 DIMENSIONAL'),
		('DM', 'DIMENSIONS'),
	)

## PRODUCT:
## Each product can be a single article product or a set (with multiple articles)
## All articles in each set can have same size and shape or they can be different
##### Evenif it's a single article product, there will still be one entry into 
#####product_varient and product_varient_article
class Av_product(models.Model):
	P_SHAPE = (
		('RD', 'ROUND SHAPED'),
		('U', 'U SHAPED'),
	)	
	product_id = models.AutoField(primary_key=True, null=False)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	shape = models.CharField(max_length = 2, null=False, choices=P_SHAPE,)
	title = models.CharField(max_length = 200, null=False)
	desc = models.CharField(max_length = 500, null=True)
	is_published = models.BooleanField(null=False, default=False)
	category_disp_priority = models.IntegerField(null = True)
	is_set = models.BooleanField(null=False, default=False)
	set_of = models.IntegerField(null = True)			## If it's a set
	is_same_size = models.BooleanField(null=False, default=False) 	## If it's a set
	is_same_shape = models.BooleanField(null=False, default=False) 	## If it's a set
	stock_image_category = models.ForeignKey(Stock_image_category, models.CASCADE, null=True) 
	featured = models.BooleanField(null=False, default=False)
	aspect_ratio = models.DecimalField(max_digits = 21, decimal_places=18, null=True) ## If its' a set and all are same size and shape in a set
	image_type =  models.CharField(max_length = 1, null=True)
	orientation = models.CharField(max_length = 20, null=True)
	max_width = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	max_height = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	min_width = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	min_height = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	publisher = models.CharField(max_length = 600, null=True)
	artist = models.CharField(max_length = 600, null=True)	
	colors = models.CharField(max_length = 600, null=True)
	key_words = models.CharField(max_length = 2000, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=True, default='')  ## If its' a set and all are same size and shape in a set
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)   ## If its' a set and all are same size and shape in a set
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)  ## If its' a set and all are same size and shape in a set
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)  ## If its' a set and all are same size and shape in a set
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)  ## If its' a set and all are same size and shape in a set
	board = models.ForeignKey(Board, models.PROTECT, null=True)  ## If its' a set and all are same size and shape in a set
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)  ## If its' a set and all are same size and shape in a set
	display_url = models.CharField(max_length = 1000, blank=True, default='')   ## A room view image
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str( self.product_id ) + " " + self.name


# Each varient of the product
class Av_product_varient(models.Model):
	product_varient_id = models.AutoField(primary_key=True, null=False)
	product = models.ForeignKey(Av_product, models.PROTECT, null=False)
	is_parent = models.BooleanField(null=False, default=True)	## Default varient in case of multiple varients
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)	
	product_varient_size_uom = models.CharField(max_length = 100, blank=False, default='DIAMETER')
	product_varient_size = models.CharField(max_length = 100, blank=True, default='')
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	url = models.CharField(max_length = 1000, blank=True, default='')   ## Default image to be shown in carts, orders
	thumbnail_url = models.CharField(max_length = 1000, blank=True, default='') ## Default thumbnail image to be shown in carts, orders
	created_date = models.DateTimeField(auto_now_add=True, null=False)
	updated_date = models.DateTimeField(auto_now=True, null=False)


# Variation images
class Av_product_varient_image(models.Model):
	product_varient_image_id = models.AutoField(primary_key=True, null=False)
	product_varient = models.ForeignKey(Av_product_varient, models.PROTECT, null=False)
	image_type = models.CharField(max_length = 2, null=False, choices=IMG_TYPE,)
	image_url = models.CharField(max_length = 1000, blank=True, default='')
	image_thumbnail_url = models.CharField(max_length = 1000, blank=True, default='')
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


# Each product article
class Av_product_varient_article(models.Model):
	product_varient_article_id = models.AutoField(primary_key=True, null=False)
	product = models.ForeignKey(Av_product, models.PROTECT, null=False)
	product_varient = models.ForeignKey(Av_product_varient, models.PROTECT, null=False)
	aspect_ratio = models.DecimalField(max_digits = 21, decimal_places=18, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)	
	size_uom = models.CharField(max_length = 100, blank=False, default='DIAMETER')
	size = models.CharField(max_length = 100, blank=True, default='')
	colors = models.CharField(max_length = 600, null=True)
	key_words = models.CharField(max_length = 2000, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=True, default='')
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True) 
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	stock_image = models.ForeignKey(Stock_image, models.PROTECT, null=False)
	
## Individual article image
class Av_product_varient_article_image(models.Model):
	product_varient_article_image_id = models.AutoField(primary_key=True, null=False)
	product_varient_article = models.ForeignKey(Av_product_varient_article, models.PROTECT, null=False)
	image_type = models.CharField(max_length = 2, null=False, choices=IMG_TYPE,)
	image_url = models.CharField(max_length = 1000, blank=True, default='')
	image_thumbnail_url = models.CharField(max_length = 1000, blank=True, default='')
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class Cart_round_artwork(Cart_item):
	av_product_variant = models.ForeignKey('Av_product_varient', models.CASCADE, null=False)
	
	
class Order_round_artwork(Order_items):
	av_product_variant = models.ForeignKey('Av_product_varient', models.CASCADE, null=False)
	
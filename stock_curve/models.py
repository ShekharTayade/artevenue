from django.db import models

# Create your models here.
class Stock_curve(models.Model):
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
	set_of = models.IntegerField(null = True)
	stock_image_category = models.ForeignKey(Stock_image_category, models.CASCADE, null=True) 
	aspect_ratio = models.DecimalField(max_digits = 21, decimal_places=18, null=True)
	colors = models.CharField(max_length = 600, null=True)
	key_words = models.CharField(max_length = 2000, null=True)
	url = models.CharField(max_length = 1000, blank=True, default='')
	thumbnail_url = models.CharField(max_length = 1000, blank=True, default='')
	moulding = models.ForeignKey("Moulding",on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey("Print_medium", models.PROTECT, null=False, default='PAPER')
	mount = models.ForeignKey("Mount", models.PROTECT, null=True)
	acrylic = models.ForeignKey("Acrylic", models.PROTECT, null=True)
	board = models.ForeignKey("Board", models.PROTECT, null=True)
	stretch = models.ForeignKey("Stretch", models.PROTECT, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str( self.product_id ) + " " + self.name


# Create your models here.
class Stock_curve_variation(models.Model):
	stock_curve_variation_id = models.AutoField(primary_key=True, null=False)
	stock_curve = models.ForeignKey(Stock_curve, models.PROTECT, null=False)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)	
	display_url = models.CharField(max_length = 1000, blank=True, default='')
	display_thumbnail_url = models.CharField(max_length = 1000, blank=True, default='')
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


from django.db import models
from artevenue.models import Stock_image_category, Product_type, Product_view, Print_medium, Moulding
from artevenue.models import Mount, Board, Acrylic, Stretch

class Room(models.Model):
	room_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 100, null=False)

class Placement(models.Model):
	placement_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 100, null=False)	

class Gallery(models.Model):
	gallery_id = models.AutoField(primary_key=True, null=False)
	title = models.CharField(max_length = 100, null=False)
	description = models.CharField(max_length = 1000, null=True)
	room = models.ForeignKey(Room, models.CASCADE, null=True)
	placement = models.ForeignKey(Placement, models.CASCADE, null=True)
	room_view_url = models.CharField(max_length = 1000, null=True)
	room_view_thumbnail_url = models.CharField(max_length = 1000, null=True)
	set_of = models.IntegerField(null = True)
	stock_image_category = models.ForeignKey(Stock_image_category, models.CASCADE, null=True) 
	category_disp_priority = models.IntegerField(null = True)
	is_published = models.BooleanField(null=False, default=False)
	colors = models.CharField(max_length = 600, null=True)
	key_words = models.CharField(max_length = 2000, null=True)

class Gallery_variation(models.Model):
	id = models.AutoField(primary_key=True, null=False)
	gallery = models.ForeignKey(Gallery, models.PROTECT, null=False)
	price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	is_parent = models.BooleanField(null=False)
	wall_area_width = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	wall_area_height = models.DecimalField(max_digits = 6, decimal_places=2, null=True)


class Gallery_item(models.Model):
	item_id = models.AutoField(primary_key=True, null=False)
	gallery = models.ForeignKey(Gallery, models.CASCADE, null=False)
	gallery_variation = models.ForeignKey(Gallery_variation, models.CASCADE, null=False)
	product_id = models.IntegerField(null=False)   ## To be referenced to Product_view
	product_name = models.CharField(max_length=500, blank=True, null=False, default = '')  ## To be referenced to Product_view
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False)
	moulding = models.ForeignKey(Moulding, models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)

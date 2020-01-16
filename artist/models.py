from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.fields import DecimalField

from artevenue.models import Ecom_site, Product_type, Original_art


class Artist_group (models.Model):
	REF_TYPE = (
		('PERCETNAGE', 'Percentage of Sale Price'),
		('FLAT', 'Flat Fee'),
	)	
	group_id = models.CharField(primary_key=True, max_length=10, null=False)
	name = models.CharField(max_length=256, blank=False,  default='')
	original_referral_fee_type = models.CharField(max_length=10, 
		choices = REF_TYPE, null=True)
	original_art_referral_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	art_print_referral_fee_type = models.CharField(max_length=10, 
		choices = REF_TYPE, null=True)
	art_print_referral_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	
	def __str__(self):
		return self.name
	
class Artist (models.Model):
	artist_id = models.AutoField(primary_key=True, max_length=10, null=False)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phone_number = models.CharField(max_length=15, blank=False, default='')
	alternate_phone_number = models.CharField(max_length=15, blank=False, default='')
	address1 = models.CharField(max_length = 1000 , blank=True, default='')
	address2 = models.CharField(max_length = 1000 , blank=True, default='')	
	city = models.CharField(max_length = 256 , blank=True, default='')
	state = models.CharField(max_length = 256 , blank=True, default='')	
	pin_code = models.CharField(max_length = 256 , blank=True, default='')	
	country = models.CharField(max_length = 256 , blank=True, default='')		
	artist_group = models.ForeignKey(Artist_group, models.SET_NULL, null=True, blank=True)
	artist_profile = models.CharField(max_length=2000, blank=False, default='')
	artist_showcase1_name = models.CharField(max_length=50, blank=False, default='')
	artist_showcase1 = models.CharField(max_length=2000, blank=False, default='')
	artist_showcase2_name = models.CharField(max_length=50, blank=False, default='')
	artist_showcase2 = models.CharField(max_length=2000, blank=False, default='')
	artist_showcase3_name = models.CharField(max_length=50, blank=False, default='')
	artist_showcase3 = models.CharField(max_length=2000, blank=False, default='')
	profile_name = models.CharField(max_length=200, blank=False, default='') ## use for diaply (ex. Jaideep Kumar)
	url_name = models.CharField(max_length=50, blank=False, default='')  ## used for creating url (ex. 'jaideep_kumar' in https://www.artevenue.com/artist/jaideep_kumar)
	profile_photo = models.ImageField(upload_to='artist/profile_photo/%Y/%m/%d/', blank=True, default="")
	profile_tagline = models.CharField(max_length=500, blank=False, default='')
	publisher = models.ForeignKey('artevenue.Publisher', models.CASCADE, null=True)
	store = models.ForeignKey('artevenue.Ecom_site', models.CASCADE, null=False)
	gallary_url = models.CharField(max_length = 1000, blank=True, default='')
	default_original_art_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	
	def __str__(self):
		return self.first_name + " " + self.last_name


class Artist_sms_email(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
	msg_type = models.CharField(max_length = 20, blank=True, default='NEW-ACCNT')
	email_sent = models.BooleanField(null=False, default=False)
	sms_sent = models.BooleanField(null=False, default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)


class Artist_stock_image (models.Model):
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
	product = models.ForeignKey('artevenue.Stock_image', models.PROTECT, null=False)

class Artist_original_art (models.Model):
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
	product = models.ForeignKey('artevenue.Original_art', models.PROTECT, null=False)

# A DB view "Artist_art_view". This holds data for all product types. 

class Artist_art_view(models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	product_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 2000, blank=True, default = '')
	price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	available_on = models.DateField(blank=True, null=True)
	updated_at = models.DateTimeField(blank=True, null=True)
	part_number = models.CharField(max_length = 30, null=True)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	is_published = models.BooleanField(null=False, default=False)
	seo_description = models.CharField(max_length = 300, null=True)
	seo_title  = models.CharField(max_length = 70, null=True)
	charge_taxes = models.BooleanField(null=False, default=False)
	featured = models.BooleanField(null=False, default=False)
	has_variants = models.BooleanField(null=False, default=False)
	aspect_ratio = models.DecimalField(max_digits = 21, decimal_places=18, null=True)
	image_type =  models.CharField(max_length = 1, null=True)
	orientation = models.CharField(max_length = 20, null=True)
	max_width = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	max_height = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	min_width = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	publisher = models.CharField(max_length = 600, null=True)
	artist = models.CharField(max_length = 600, null=True)
	colors = models.CharField(max_length = 600, null=True)
	key_words = models.CharField(max_length = 2000, null=True)
	url = models.CharField(max_length = 1000, blank=True, default='')
	thumbnail_url = models.CharField(max_length = 1000, blank=True, default='')
	session_id = models.CharField(max_length = 40, blank=True, default='')
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	image_to_frame = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, default="")
	image_to_frame_thumbnail = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, default="")
	status = models.CharField(max_length = 3, blank=True, null=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	collage_layout_id = models.IntegerField(null=True)
	high_resolution_url = models.CharField(max_length = 1000, blank=True, default='')
	art_width = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	art_height = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	art_medium = models.CharField(max_length = 3, blank=True, default='')
	art_surface = models.CharField(max_length = 3, blank=True, default='')
	art_surface_desc = models.CharField(max_length = 500, blank=True, default='')
	category_disp_priority = models.IntegerField(null = True)
	art_print_allowed = models.BooleanField(null=False, default=False)
	original_art_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	available_qty = models.IntegerField(null=False)	
	sold_qty = models.IntegerField(null=True)	
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)
	
	class Meta:
		managed = False
		db_table = 'artist_art_view'

class Inventory_udate(models.Model):
	product = models.ForeignKey(Original_art, models.PROTECT, null=False)
	product_type = models.ForeignKey('artevenue.Product_type', null=True, on_delete=models.SET_NULL)
	update_qty = models.IntegerField(null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.product) + str(updated_qty)

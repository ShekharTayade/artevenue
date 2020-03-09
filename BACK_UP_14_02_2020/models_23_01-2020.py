from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.fields import DecimalField

from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from PIL import Image, ExifTags
from io import StringIO, BytesIO
from django.conf import settings


class Ecom_site(models.Model):
	store_id = models.AutoField(primary_key=True, null=False)
	html_meta_title = models.CharField(max_length = 256, blank=False, unique=True)
	html_meta_name = models.CharField(max_length = 256, blank=True, default='')	
	seo_keywords = models.CharField(max_length = 256, blank=True, default='')	
	store_name = models.CharField(max_length = 100, blank=False)	
	tag_line = models.CharField(max_length = 50, blank=True, default='')
	show_copyright = models.BooleanField(null=False, default=False)
	copyright_year = models.CharField(max_length = 4, blank=True, default='')
	store_address1 = models.CharField(max_length = 1000 , blank=True, default='')
	store_address2 = models.CharField(max_length = 1000 , blank=True, default='')	
	store_city = models.CharField(max_length = 256 , blank=True, default='')
	store_state = models.CharField(max_length = 256 , blank=True, default='')	
	store_zip = models.CharField(max_length = 256 , blank=True, default='')	
	store_country = models.CharField(max_length = 256 , blank=True, default='')		
	#store_email_id =  models.EmailField(null=True)
	phone_support_available = models.BooleanField(null=False, default=False)
	support_phonenumber = models.CharField(max_length = 50, blank=True, default='')
	phone_support_start_time = models.TimeField(blank=True, null=True)
	phone_support_end_time = models.TimeField(blank=True, null=True)
	phone_support_days = models.CharField(max_length = 50, blank=True, default='')
	show_promotion_section = models.BooleanField(null=False, default=False)
	number_of_promotion_slides = models.IntegerField(null=True, blank=True)
	show_featured_section = models.BooleanField(null=False, default=False)
	featured_header = models.CharField(max_length = 50, blank=True, default='')
	number_of_featured_slides = models.IntegerField(null=True, blank=True)
	show_frame_my_art_section = models.BooleanField(null=False, default=False)
	frame_my_art_header = models.CharField(max_length = 50 , blank=True, default='')
	number_of_frame_my_art_slides = models.IntegerField(null=True, blank=True)
	email_support_enabled = models.BooleanField(null=False, default=False)
	support_email = models.EmailField(null=True)
	gst_number = models.CharField(max_length = 30 , blank=True, default='')
	pan_number = models.CharField(max_length = 30 , blank=True, default='')
	tan_number = models.CharField(max_length = 30 , blank=True, default='')

	def __str__(self):
		return str(self.store_id)

	
class Contact_us(models.Model):
	first_name = models.CharField(max_length=150, blank=False, null =False)
	last_name = models.CharField(max_length=150, blank=False, null =False)
	email_id = models.EmailField(blank=False, null=False)
	phone_number = models.CharField(max_length=30, blank=True, default='')
	subject = models.CharField(max_length=200, blank=False, null =False)
	message = models.CharField(max_length=4000, blank=False, null =False)
	msg_datetime = models.DateTimeField(null=True, auto_now_add=True, editable=False)
	response = models.CharField(max_length=4000, blank=True, default='',editable=False)
	resp_datetime = models.DateTimeField(null=True, editable=False)
	reponded_by = models.CharField(max_length=30, blank=True, default='', editable=False)
	email_sent_to_artevenue = models.BooleanField(null=False, default=False)
	email_sent_to_sender = models.BooleanField(null=False, default=False)
	sms_sent_to_artevenue = models.BooleanField(null=False, default=False)
	sms_sent_to_sender = models.BooleanField(null=False, default=False)
	
	def __str__(self):
		return self.first_name + " " + self.last_name 
		
	
# Model - voucher
# This model stores vouchers that the Store grants.	
class Voucher(models.Model):
	voucher_id = models.AutoField(primary_key=True, null=False)
	voucher_code = models.CharField(max_length = 20, null=False)
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	discount_type = models.CharField(max_length = 10, null=False)  # PERCETNAGE or CASH
	discount_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	all_applicability = models.BooleanField(null=False, default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	expiry_date = models.DateField(blank=True, null=True)

	class meta:
		unique_together = (('store', 'voucher_id', 'effective_from', 'discount_type'),)
    
	def __str__(self):
		return self.voucher_code

class Voucher_user(models.Model):
	voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, null=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	used_date = models.DateField(blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	class meta:
		unique_together = (('voucher', 'user'),)

	def __str__(self):
		return str(self.user) + '-' + str(self.voucher)


class Voucher_used(models.Model):
	voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, null=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.user) + '-' + str(self.voucher)


class Egift_card_design(models.Model):
	design_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, blank=True, default='')
	description = models.CharField(max_length = 1000, blank=True, default='')
	url = models.CharField(max_length = 256, null=True)
	amount_from = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	amount_to =models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	text_location = models.CharField(max_length = 20, blank=True, default='') # 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'; # Location to print the text on the card
	text_color = models.CharField(max_length = 20, blank=True, default='')
	voucher_location = models.CharField(max_length = 20, blank=True, default='')

	def __str__(self):
		return self.name + '(' + str(self.design_id) + ')'	
		
class Egift(models.Model):
	TRN_STATUS = (
		('PP', 'Payment Pending'),
		('PC', 'eGift Pending to be Redeemed'),
		('PM', 'Partial Redemption Done'),
		('RC', 'eGift Order Comleted - Redemption done'),
		('EX', 'eGift Order Expired'),
	)	
	gift_rec_id = models.AutoField(primary_key=True, null=False)
	giver = models.ForeignKey(User, on_delete=models.CASCADE, null=False,
			related_name='egift_giver' )
	receiver_name = models.CharField(max_length = 600, blank=False, default='')
	receiver_email = models.EmailField(blank=False, null=False) 
	receiver_phone = models.CharField(max_length=30, blank=True, null=True, 
		help_text = "Optional: Will help us to reach the receiver in case of any issues")
	delivery_date = models.DateField(blank=True, null=True)
	gift_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	message = models.CharField(max_length = 2000, blank=True, default='')
	egift_card_design = models.ForeignKey(Egift_card_design, on_delete=models.CASCADE, null=True)
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
			related_name='egift_receiver')
	voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, null=True)
	payment_status = models.CharField(max_length = 2, 
		blank=True, choices=TRN_STATUS, default='PP') # PP (payment pending), PC (payment complete), PR(pending redemption), PC (partial redemption), RC (redemption complete)
	gift_date = models.DateField(blank=True, null=True)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	giver_email_sent = models.DateTimeField(null=True)
	receiver_email_sent = models.DateTimeField(null=True)
	card_image = models.ImageField(upload_to='egift_cards/%Y/%m/%d/', blank=True, default="")

	def __str__(self):
		return str(self.giver) + ' To ->' + self.receiver_name	

class eGift_sms_email(models.Model):
	egift = models.OneToOneField(Egift, on_delete=models.CASCADE, null=False)
	receiver_email_sent = models.BooleanField(null=False, default=False)
	giver_email_sent = models.BooleanField(null=False, default=False)
	receiver_sms_sent = models.BooleanField(null=False, default=False)
	giver_sms_sent = models.BooleanField(null=False, default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)		

	def __str__(self):
		return str(self.egift)
	
class Egift_redemption(models.Model):
	redemption_id = models.AutoField(primary_key=True, null=False)
	egift = models.ForeignKey(Egift, on_delete=models.CASCADE, null=False)
	redemption_date = models.DateField(blank=True, null=True)
	redemption_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	
class New_arrival(models.Model):
	new_arival_id = models.AutoField(primary_key=True, null=False)
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	product_tag = models.CharField(max_length = 20, blank=True, default='')
	discount_type = models.CharField(max_length = 10, null=False)  # PERCETNAGE or CASH
	discount_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

	def __str__(self):
		return self.new_arrival_id
	
	
class New_arrival_images(models.Model):
	image_id = models.AutoField(primary_key=True, null=False)
	new_arrival = models.ForeignKey(New_arrival, models.CASCADE)
	image_name = models.CharField(max_length = 1000, blank=True, default='')

	def __str__(self):
		return self.image_name
	
	class Meta:
		unique_together = ("image_id", "new_arrival")

## This drives the main slider on the site. It sequences the contents from Promotions 
# and New Arrivals models		
class Main_slider(models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	id = models.AutoField(primary_key=True, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	new_arrival_seq = models.IntegerField(null=True, blank=True)
	promotion_seq = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return self.id


class Menu(models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	id = models.AutoField(primary_key=True, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	name = models.CharField(max_length = 128, null=False)
	level = models.IntegerField(null=False)  # level 0 is main menu
	parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        on_delete=models.CASCADE) # Should be id field of the parent
	sort_order = models.IntegerField(null=False)
	url = models.CharField(max_length = 256, null=True)
	
	def __str__(self):
		return self.name

		
class Country(models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	country_code = models.CharField(max_length=80, primary_key = True) 
	country_name = models.CharField(max_length=100, blank = True, null=True, unique=True)

	def __str__(self):
		return self.country_name

class State(models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	state_code = models.CharField(max_length=100, primary_key = True) 
	state_name = models.CharField(max_length=100, blank = True, null=True, unique=True)
	country = models.ForeignKey(Country, models.CASCADE, null=False)

	def __str__(self):
		return self.state_code

class City(models.Model):
	city = models.CharField(max_length=100, primary_key = True) 
	state = models.ForeignKey(State, models.CASCADE, null=False)

	def __str__(self):
		return self.city

	
class Pin_code(models.Model):
	pin_code = models.CharField(primary_key = True, max_length=10, null=False)


class Pin_city_state_country(models.Model):
	pin_code = models.ForeignKey(Pin_code, models.CASCADE, null=False)
	taluk =  models.CharField(max_length=500, null = True)
	city = models.ForeignKey(City, models.CASCADE, null=False) 
	state  = models.ForeignKey(State, models.CASCADE, null=False)
	country  = models.ForeignKey(Country, models.CASCADE, null=False)
	
	class Meta:
		unique_together = ("pin_code", "city", "taluk", "state", "country")
	def __str__(self):
		return self.pin_code

		
	
class Shipping_method (models.Model):
	shipping_method_id = models.AutoField(primary_key=True, null=False)
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	name = models.CharField(max_length = 128, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)

	def __str__(self):
		return self.name

class Shipping_cost_slabs (models.Model):
	slab_from = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	slab_to = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	flat_shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	
	
class Shipper (models.Model):
	shipper_id = models.AutoField(primary_key=True, null=False)
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	name = models.CharField(max_length = 128, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)

	def __str__(self):
		return self.name
	
	
class Shipper_shipping_method (models.Model):
	shipper_shipping_method = models.AutoField(primary_key=True, null=False) 
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	shipper = models.ForeignKey(Shipper, models.CASCADE, null=False)
	shipping_method_id = models.ForeignKey(Shipping_method, models.CASCADE, null=False)
	rate_type = models.CharField(max_length = 128, null=False) #KG (per KG), #SQFT (per Sqft) etc.....
	rate = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)

	def __str__(self):
		return self.shipper
	

class Shipping_status (models.Model):
	shipping_status_id = models.AutoField(primary_key=True, null=False)
	shipping_status_code = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 1000, null=True)

	def __str__(self):
		return self.shipping_status_code

	
class  User_billing_address (models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	billing_address_id = models.AutoField(primary_key=True, null=False)
	full_name = models.CharField(max_length=600, blank=False, null=False)
	company = models.CharField(max_length=600, blank=True, default='')
	gst_number = models.CharField(max_length=30, blank=True, default='')
	address_1 = models.CharField(max_length=600, blank=False, null=False)
	address_2 = models.CharField(max_length=600, blank=True, default='')
	land_mark = models.CharField(max_length=600, blank=True, default='')
	city = models.CharField(max_length=600, blank=False, null=False)
	state = models.ForeignKey(State, on_delete = models.PROTECT, null=True)
	pin_code = models.ForeignKey(Pin_code, on_delete = models.PROTECT, null=True)
	country = models.ForeignKey(Country, on_delete = models.PROTECT, null=False, default= "IND")
	phone_number = models.CharField(max_length=30, blank=True, default='')
	email_id = models.EmailField(blank=True, default='')
	pref_addr = models.NullBooleanField(null=True, default=False)
	updated_date =  models.DateField(blank=True, null=True)

	def __str__(self):
		return self.user

	
class  User_shipping_address (models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	shipping_address_id = models.AutoField(primary_key=True, null=False)
	full_name = models.CharField(max_length=500, blank=False, null=False)
	company = models.CharField(max_length=600, blank=True, default='')
	address_1 = models.CharField(max_length=600, blank=False, null=False)
	address_2 = models.CharField(max_length=600, blank=True, default='')
	land_mark = models.CharField(max_length=600, blank=True, default='')
	city = models.CharField(max_length=600, blank=False, null=False)
	state = models.ForeignKey(State, on_delete = models.PROTECT, null=True)
	pin_code = models.ForeignKey(Pin_code, on_delete = models.PROTECT, null=True)
	country = models.ForeignKey(Country, on_delete = models.PROTECT, null=False, default= "IND")
	phone_number = models.CharField(max_length=30, blank=True, default='')
	email_id = models.EmailField(blank=True, default='')
	pref_addr = models.NullBooleanField(null=True, default=False)
	updated_date =  models.DateField(blank=True, null=True)

	def __str__(self):
		return self.user

class Price_type(models.Model):
	price_type = models.CharField(primary_key=True, max_length = 20, null=False) # RIN (Running inch), SIN (Square Inch)
	description = models.CharField(max_length = 1000, null=True)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)	

	def __str__(self):
		return self.price_type
		

class Tax (models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	tax_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	tax_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)

	def __str__(self):
		return self.name

# Abstrct, People, Animals, Landscape, Portrait etc....
class Stock_image_category(models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	category_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 1000, null=True)
	background_image = models.CharField(max_length = 1000, blank=True, default='')
	parent = models.ForeignKey(
		'self', null=True, blank=True, related_name='children',
		on_delete=models.CASCADE)
	trending = models.BooleanField(null=False, default=False)
	url = models.CharField(max_length = 1000, blank=True, default='')
	featured_collection = models.BooleanField(null=False, default=False)

	def __str__(self):
		return self.name
	
	class Meta:
		unique_together = ("store", "category_id", "name")


# Stock Image, User Image, Stock Collage, Original Art etc...etc....	
class Product_type(models.Model):
	TYPE_CHOICES = (
		('STOCK-IMAGE', 'Stock Image'),
		('USER-IMAGE', 'User Uploaded Image'),
		('STOCK-COLLAGE', 'Stock Collage Layout'),
		('ORIGINAL-ART', 'Original Art'),
		('FRAME', 'Frame')
	)	

	store = models.ForeignKey(Ecom_site, models.CASCADE)
	product_type_id = models.CharField(primary_key=True, max_length=20, 
		choices=TYPE_CHOICES)
	is_shipping_required = models.BooleanField(null=False, default=False)
	tax = models.ForeignKey(Tax, models.CASCADE, null=True)
	apply_inventory = models.BooleanField(null=False, default=False)

	def __str__(self):
		return self.product_type_id		
		
		
class Stock_image(models.Model):
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
	category_disp_priority = models.IntegerField(null = True)

	def __str__(self):
		return str( self.product_id ) + " " + self.name
		
class User_image (models.Model):
	product_id = models.AutoField(primary_key=True, null=False)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	session_id = models.CharField(max_length = 40, blank=True, default='') # to store the session_key in case of anonymous user
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	image_to_frame = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, default="")
	status = models.CharField(max_length = 3, blank=True, null=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)
	updated_date = models.DateTimeField(auto_now=True, null=False)
	image_to_frame_thumbnail = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, default="")
	category_disp_priority = models.IntegerField(null = True)
	def __str__(self):
		return str( self.product_id ) + " " + self.image_to_frame.name

	def create_thumbnail(self):
		# If there is no image associated with this.
		# do not create thumbnail
		if not self.image_to_frame:
			return

		# Set our max thumbnail size in a tuple (max width, max height)
		THUMBNAIL_SIZE = (75, 75)

		'''
		DJANGO_TYPE = self.image_to_frame.file.content_type

		if DJANGO_TYPE == 'image/jpeg':
			PIL_TYPE = 'jpeg'
			FILE_EXTENSION = 'jpg'
		elif DJANGO_TYPE == 'image/png':
			PIL_TYPE = 'png'
			FILE_EXTENSION = 'png'
		elif DJANGO_TYPE == 'image/gif':
			PIL_TYPE = 'gif'
			FILE_EXTENSION = 'gif'
		'''
		
		PIL_TYPE = ''
		if self.image_to_frame.name.lower().endswith(".jpg"):
			PIL_TYPE = 'jpeg'
			FILE_EXTENSION = 'jpg'
			DJANGO_TYPE = 'image/jpeg'
		if self.image_to_frame.name.lower().endswith(".png"):
			PIL_TYPE = 'png'
			FILE_EXTENSION = 'png'
			DJANGO_TYPE = 'image/png'
		if self.image_to_frame.name.lower().endswith(".gif"):
			PIL_TYPE = 'gif'
			FILE_EXTENSION = 'gif'
			DJANGO_TYPE = 'image/gif'
		if PIL_TYPE == '' :
			extension = os.path.splitext(self.image_to_frame.name)[1]
			PIL_TYPE = extension.lower()[1:]
			FILE_EXTENSION = PIL_TYPE
			DJANGO_TYPE = 'image/' + PIL_TYPE[1:]

		# Open original photo which we want to thumbnail using PIL's Image
		image = Image.open(self.image_to_frame)

		# use our PIL Image object to create the thumbnail, which already
		image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

		# Save the thumbnail
		#temp_handle = StringIO()
		temp_handle = BytesIO()
		image.save(temp_handle, PIL_TYPE)
		temp_handle.seek(0)
		
		# Save image to a SimpleUploadedFile which can be saved into ImageField
		from django.core.files.uploadedfile import SimpleUploadedFile
		suf = SimpleUploadedFile(os.path.split(self.image_to_frame.name)[-1],
								 temp_handle.read(), content_type=DJANGO_TYPE)
		# Save SimpleUploadedFile into image field
		self.image_to_frame_thumbnail.save(
			'%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
			suf, save=False)

	def save(self, *args, **kwargs):
		self.create_thumbnail()
		super(User_image, self).save()	

class Stock_collage(models.Model):
	product_id = models.AutoField(primary_key=True, null=False)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	collage_layout = models.ForeignKey('Collage_layout', models.CASCADE, null=False)
	name = models.CharField(max_length = 200, null=False)
	is_published = models.BooleanField(null=False, default=False)
	category_disp_priority = models.IntegerField(null = True)

	def __str__(self):
		return str( self.product_id ) + " " + self.name
	
class Original_art(models.Model):
	IMAGE_TYPE = (
		('ART', 'Art Work'),
		('PHT', 'Photograph'),
	)
	MEDIUM = (
		('OIL', 'Oil'),
		('ACR', 'Acrylic'),
		('WTR', 'Water Color'),
		('GOU', 'Gouache'),
		('INK', 'Ink'),
		('PEN', 'Pen'),
		('PST', 'Pastel'),
		('PNC', 'Pencil'),
		('COL', 'Charcoal'),
	)
	SURFACE = (
		('CVS', 'CANVAS'),
		('PPR', 'PAPER'),
		('FAB', 'FABRIC'),	
		('GLS', 'GLASS'),	
		('WOD', 'WOOD'),	
	)
	product_id = models.AutoField(primary_key=True, null=False)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	name = models.CharField(max_length = 200, null=False)
	description = models.CharField(max_length = 2000, blank=True, default = '')
	price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	available_on = models.DateField(blank=True, null=True)
	part_number = models.CharField(max_length = 30, null=True)
	is_published = models.BooleanField(null=False, default=False)
	seo_description = models.CharField(max_length = 300, null=True)
	seo_title  = models.CharField(max_length = 70, null=True)
	charge_taxes = models.BooleanField(null=False, default=False)
	featured = models.BooleanField(null=False, default=False)
	has_variants = models.BooleanField(null=False, default=False)
	aspect_ratio = models.DecimalField(max_digits = 21, decimal_places=18, null=True)
	image_type =  models.CharField(max_length = 1, null=True, choices = IMAGE_TYPE)
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
	high_resolution_url = models.CharField(max_length = 1000, blank=True, default='')
	art_width = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	art_height = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
	art_medium = models.CharField(max_length = 3, blank=True, default='',
		choices=MEDIUM)
	art_surface = models.CharField(max_length = 3, blank=True, default='',
		choices=SURFACE)
	art_surface_desc = models.CharField(max_length = 500, blank=True, default='')
	category_disp_priority = models.IntegerField(null = True)

	def __str__(self):
		return self.name + " - By " + self.artist


class Stock_image_stock_image_category(models.Model):
	stock_image = models.OneToOneField(Stock_image, models.PROTECT, null=False)
	stock_image_category = models.ForeignKey(Stock_image_category, models.CASCADE, null=True) 


class Original_art_original_art_category(models.Model):
	original_art = models.OneToOneField(Original_art, models.PROTECT, null=False)
	stock_image_category = models.ForeignKey(Stock_image_category, models.CASCADE,
	null=True, related_name="original_art_category") 

	
class Collage_layout(models.Model):
	collage_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 200, null=False)
	moulding = models.ForeignKey('Moulding', models.PROTECT, null=True)

	def __str__(self):
		return self.name + str(moulding)


# A DB view "product_view". This holds data for all product types. 
class Product_view(models.Model):
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
	
	class Meta:
		managed = False
		db_table = 'product_view'	

class Curated_category(models.Model):
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	category_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 2000, blank=True, default = '')
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)

	def __str__(self):
		return str(self.category_id) + '-' + self.name
	
class Curated_collection(models.Model):
	curated_category = models.ForeignKey(Curated_category, models.DO_NOTHING)
	product = models.ForeignKey(Stock_image, models.DO_NOTHING)
	product_type = models.ForeignKey(Product_type, models.DO_NOTHING, null=False) 

	def __str__(self):
		return str(self.curated_category) + ' -> ' + str(self.product)
	
#################################################################################
#     Promotions
###################
# Model - promotion
# This model stores promotions that the Store runs.	
# New Arrival, Sale, Promotion etc...
class Promotion(models.Model):
	STORE_WIDE = 'A'
	CATEGORY_WIDE = 'C'
	SELECT_PRODS = 'P'
	PROMO_TYPE = (
		(STORE_WIDE, 'Store-wide Promotion, applies to all products'),
		(CATEGORY_WIDE, 'Applies to a particular category'),
		(SELECT_PRODS, 'Applies to select products only'),
	)

	promotion_id = models.AutoField(primary_key=True, null=False)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=False) 
	name = models.CharField(max_length = 600, blank = True, default = '')
	store = models.ForeignKey(Ecom_site, models.CASCADE)
	promotion_type = models.CharField(max_length = 1, choices = PROMO_TYPE, blank = True, default = '')
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	discount_type = models.CharField(max_length = 10, null=False)  # PERCETNAGE or CASH
	discount_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

	class meta:
		unique_together = (('store', 'promotion_id', 'effective_from', 'product_tag', 'discount_type'),)
	def __str__(self):
		return str(self.promotion_id) + '-' + self.name

class Promotion_voucher(models.Model):
	promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=False)
	voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, null=False)
	show_popup = models.BooleanField(null=False, default=False)
	pop_at_start = models.BooleanField(null=False, default=False)	
	pop_at_close = models.BooleanField(null=False, default=False)
	popup_duration = models.TimeField(null=True)
	
class Promotion_images(models.Model):
	image_id = models.AutoField(primary_key=True, null=False)
	promotion = models.ForeignKey(Promotion, models.CASCADE)
	image_name = models.CharField(max_length = 1000, blank=True, default='')

	class Meta:
		unique_together = ("image_id", "promotion")
	def __str__(self):
		return self.image_name

class Promotion_stock_image(models.Model):
	promotion = models.ForeignKey(Promotion, models.CASCADE, null=False)
	stock_image = models.ForeignKey(Stock_image, models.CASCADE, null=False)

	def __str__(self):
		return str(self.promotion_id)
		
	class Meta:
		unique_together = ("promotion", "stock_image")	

class Promotion_stock_collage(models.Model):
	promotion = models.ForeignKey(Promotion, models.CASCADE, null=False)
	stock_collage = models.ForeignKey(Stock_collage, models.CASCADE, null=False)

	def __str__(self):
		return str(self.promotion_id)
		
	class Meta:
		unique_together = ("promotion", "stock_collage")	

class Promotion_original_art(models.Model):
	promotion = models.ForeignKey(Promotion, models.CASCADE, null=False)
	original_art = models.ForeignKey(Original_art, models.CASCADE, null=False)

	def __str__(self):
		return str(self.promotion_id)
		
	class Meta:
		unique_together = ("promotion", "original_art")	

class Promotion_moulding(models.Model):
	promotion = models.ForeignKey(Promotion, models.CASCADE, null=False)
	moulding = models.ForeignKey('Moulding', models.CASCADE, null=False)

	def __str__(self):
		return str(self.promotion_id)
		
	class Meta:
		unique_together = ("promotion", "moulding")	

## A DB view. For holding product promotions for all product types (except USER-IMAGE)
class Promotion_product_view(models.Model):
	id = models.AutoField(primary_key=True)
	promotion = models.ForeignKey(Promotion, models.CASCADE, null=False)
	product_id = models.IntegerField(null=False)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=False) 
	
	class Meta:
		managed = False
		db_table = 'promotion_product_view'	
		
###################
#  END:  Promotions
###################


#################################################################################
#  FRAMING COMPONENTS 
###################
class Mount (models.Model):
	mount_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 2000, null=False, default="")
	type = models.CharField(max_length = 30, blank='', default = '')
	color = models.CharField(max_length = 30, null=False)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	price_type = models.ForeignKey(Price_type, models.CASCADE, null=True)

	def __str__(self):
		return self.name
	
	
class Board (models.Model):
	board_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 2000, null=False, default="")
	type = models.CharField(max_length = 30, blank='', default = '')
	color = models.CharField(max_length = 30, null=False)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	price_type = models.ForeignKey(Price_type, models.CASCADE, null=True)

	def __str__(self):
		return self.name
	
	
class Acrylic (models.Model):
	acrylic_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 2000, null=False, default="")
	type = models.CharField(max_length = 30, blank='', default = '')
	color = models.CharField(max_length = 30, null=False)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	price_type = models.ForeignKey(Price_type, models.CASCADE, null=True)

	def __str__(self):
		return self.name

	
class Print_medium(models.Model):
	medium_id = models.CharField(primary_key=True, max_length = 30)
	description = models.CharField(max_length = 1000, blank=True, default = '')
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	price_type = models.ForeignKey(Price_type, models.CASCADE, null=True)

	def __str__(self):
		return self.medium_id

class Stretch (models.Model):
	stretch_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 2000, null=False, default="")
	type = models.CharField(max_length = 30, blank='', default = '')
	color = models.CharField(max_length = 30, null=False)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	price_type = models.ForeignKey(Price_type, models.CASCADE, null=True)

	def __str__(self):
		return self.name
		
	
class Moulding(models.Model):
	PAPER = 'P'
	CANVAS = 'C'
	BOTH = 'B'
	APPLIES_TO = (
		(PAPER, 'Applies to Paper Only'),
		(CANVAS, 'Applies to Canvas Only'),
		(BOTH, 'Applies to Paper and Canvas'),
	)
	
	moulding_id = models.CharField(primary_key=True, null=False, max_length = 20,)
	name = models.CharField(max_length = 128, null=False)
	description = models.CharField(max_length = 1000, blank=True, default = '')
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	price_type = models.ForeignKey(Price_type, models.CASCADE, null=True)
	width_inner_inches = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	width_inches = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	depth_inches = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	available_on = models.DateField(blank=True, null=True)
	updated_at = models.DateTimeField(blank=True, null=True)
	part_number = models.CharField(max_length = 30, null=True)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	is_published = models.BooleanField(null=False, default=False)
	seo_description = models.CharField(max_length = 300, null=True)
	seo_title  = models.CharField(max_length = 70, null=True)
	charge_taxes = models.BooleanField(null=False, default=False)
	tax = models.ForeignKey(Tax, models.CASCADE, null=True)
	tax_rate = models.CharField(max_length = 120, null=True)
	featured = models.BooleanField(null=False, default=False)
	has_variants = models.BooleanField(null=False, default=False)
	applies_to = models.CharField(max_length = 1, null=False, choices=APPLIES_TO, default=BOTH)

	def __str__(self):
		return self.name

	
# store images for a Mouldings
class Moulding_image(models.Model):
	moulding = models.ForeignKey(Moulding, models.CASCADE, null=False)
	image_id = models.AutoField(primary_key=True, null=False)
	image_type = models.CharField(max_length = 20, blank=True, default='') # SHOW, APPLY
	url = models.CharField(max_length = 1000, blank=True, default='')
	border_slice = models.CharField(max_length = 10, blank=True, default='')

	def __str__(self):
		return self.moulding
	
	class Meta:
		unique_together = ("moulding", "image_type")	
		
###########################
#  END:  FRAMING COMPONENTS
###########################



#################################################################################
#  CART 
###################
class Cart(models.Model):
	CART_STATUS = (
		('AC', 'Active'),
		('AB', 'Abandoned'),
		('CO', 'Checked Out'),
	)
	
	
	cart_id = models.AutoField(primary_key=True, null=False)
	store = models.ForeignKey(Ecom_site, models.PROTECT)
	session_id = models.CharField(max_length = 40, blank=True, default='') # to store the session_key in case of anonymous user
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
	voucher = models.ForeignKey(Voucher, models.PROTECT, null=True)
	voucher_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	referral = models.ForeignKey('Referral', on_delete=models.PROTECT, null=True)
	referral_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	quantity = models.IntegerField(null=True)
	cart_unit_price = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	cart_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	cart_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	cart_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	cart_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	cart_status = models.CharField(max_length = 2, blank=True, default='AC',
		choices=CART_STATUS, )
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	ip_address = models.CharField(max_length = 50, blank=True, default = '' )
	def __str__(self):
		return str(self.cart_id)

	class Meta:
		unique_together = ("cart_id", "session_id", "user")	
		
# An abstract class for Cart Item	
class Cart_item(models.Model):
	cart_item_id = models.AutoField(primary_key=True, null=False) 
	cart = models.ForeignKey('Cart', models.CASCADE, null=False) 
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	class Meta:
		abstract = True
	class Meta:
		unique_together = ("cart_item_id", "cart")	
		
class Cart_stock_image(Cart_item):
	stock_image = models.ForeignKey('Stock_image', models.CASCADE, null=False)

class Cart_user_image(Cart_item):
	user_image = models.ForeignKey('User_image', models.CASCADE, null=False)

class Cart_stock_collage(Cart_item):
	stock_collage = models.ForeignKey('Stock_collage', models.CASCADE, null=False)

class Cart_original_art(Cart_item):
	original_art = models.ForeignKey('Original_art', models.CASCADE, null=False)

	
####### A DB View for Cart_item_view : This will hold all the cart items 
class Cart_item_view(models.Model):
	cart_item_id = models.AutoField(primary_key=True, null=False) 
	cart = models.ForeignKey('Cart', models.DO_NOTHING, null=False) 
	product = models.ForeignKey(Product_view, models.PROTECT, null=False)
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False) 
	
	class Meta:
		managed = False
		db_table = 'cart_item_view'	
###################
#  END:  CART
###################



#############################################################################
#  Stock Image Pricing
############################
class Publisher (models.Model):
	publisher_id = models.CharField(primary_key=True, max_length=10, null=False)
	publisher_name = models.CharField(max_length=256, blank=False,  default='')
	publisher_group = models.CharField(max_length=256, null=True)

	def __str__(self):
		return self.publisher_name

	
class Publisher_price (models.Model):
	publisher_price_id = models.AutoField(primary_key=True, null=False)
	publisher = models.ForeignKey(Publisher, models.CASCADE, max_length=10, null=False)
	print_medium = models.ForeignKey(Print_medium, models.CASCADE, null=False, default='PAPER')
	price_type = models.ForeignKey(Price_type, models.CASCADE, null=True)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	
	class Meta:
		unique_together = ("publisher", "print_medium", "price_type")	
		
	def __str__(self):
		return str(self.publisher)
############################
#  END:  Stock Image Pricing
############################
	

#############################################################################
#  	Business User
############################
class Profile_group (models.Model):
	profile_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length=30, blank=True)
	description = models.CharField(max_length=30, blank=True)
	discount_type = models.CharField(max_length=30, blank=True)
	discount_percentage = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)	

	def __str__(self):
		return self.name
	
class Business_profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, related_name="business_user")
	contact_name = models.CharField(max_length=500, blank=False)
	company =  models.CharField(max_length=30, blank=True)
	profile_group = models.ForeignKey(Profile_group, models.CASCADE, null=True)
	address_1 = models.CharField(max_length=600, blank=False, null=False)
	address_2 = models.CharField(max_length=600, blank=True, default='')
	city = models.CharField(max_length=600, blank=False, null=False)
	state = models.ForeignKey(State, on_delete = models.PROTECT, null=False)
	pin_code = models.ForeignKey(Pin_code, on_delete = models.PROTECT, null=True)
	country = models.ForeignKey(Country, on_delete = models.PROTECT, null=False, default= "IND")
	phone_number = models.CharField(max_length=30, blank=False, null=False)
	# email_id  = models.EmailField(blank=True, default='')  -- Same as 'User' email
	gst_number = models.CharField(max_length=30, blank=True, default='')
	tax_id = models.CharField(max_length=30, blank=True, default='')
	approval_date = models.DateField(blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	bank_acc_no = models.CharField(max_length = 20, default = '', blank = True)
	ifsc_code = models.CharField(max_length = 11, default = '', blank = True)
	bank_name = models.CharField(max_length = 500, default = '', blank = True)
	bank_branch = models.CharField(max_length = 600, default = '', blank = True)


	def __str__(self):
		return self.company + " - " + self.contact_name
	

class Business_commission(models.Model):
	month_year = models.CharField(max_length = 7, blank = False, 
		null = False, help_text='Commission month (YYYY-MM)')
	business_profile = models.ForeignKey(Business_profile, 
		on_delete=models.CASCADE, null=False)
	commission_amount = models.DecimalField(max_digits=12, 
		decimal_places=2, blank=False, null=False)
	sale_in_current_year = models.DecimalField(max_digits=12, 
		decimal_places=2, blank=False, null=False)
	commission_paid_date = models.DateTimeField(null=True)
	commission_paid_reference =models.CharField(max_length = 600, 
		default = '', blank = True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	
############################
#  END:  Business User
############################

	

#############################################################################
#  	ORDER
############################	
class Order (models.Model):
	ORD_STATUS = (
		('PP', 'Payment Pending'),
		('PC', 'In Process'),
		('PR', 'In Production'),
		('SH', 'Ready for Shipping'),
		('IN', 'In Transit'),
		('CO', 'Delivered'),
	)

	order_id = models.AutoField(primary_key=True, null=False)
	order_number = models.CharField(max_length = 15, blank = True, default = '')
	order_date =  models.DateField(blank=True, null=True)
	cart = models.ForeignKey(Cart,on_delete=models.PROTECT, null=False)
	store = models.ForeignKey(Ecom_site, models.PROTECT)
	session_id = models.CharField(max_length = 40, blank=True, default='') # to store the session_key in case of anonymous user
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
	voucher = models.ForeignKey(Voucher, models.PROTECT, null=True)
	voucher_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	referral = models.ForeignKey('Referral', on_delete=models.PROTECT, null=True)
	referral_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	quantity = models.IntegerField(null=True)
	sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	order_discount_amt = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	tax = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	order_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	shipping_method = models.ForeignKey(Shipping_method, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup
	shipper = models.ForeignKey(Shipper, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup	
	shipping_status = models.ForeignKey(Shipping_status, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup
	order_status = models.CharField(max_length = 2, blank=True, 
		choices=ORD_STATUS, default='PP') 
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	invoice_number = models.CharField(max_length = 15, blank = True, default = '')
	invoice_date = models.DateTimeField(null=True)
	
	def __str__(self):
		return str(self.order_id) + ' - ' + str(self.user)

class Order_sms_email(models.Model):
	order = models.OneToOneField(Order, on_delete=models.CASCADE, null=False)
	customer_email_sent = models.BooleanField(null=False, default=False)
	factory_email_sent = models.BooleanField(null=False, default=False)
	customer_sms_sent = models.BooleanField(null=False, default=False)
	factory_sms_sent = models.BooleanField(null=False, default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)
	
	def __str__(self):
		return str(self.order)
		
class Order_items (models.Model):
	order_item_id = models.AutoField(primary_key=True, null=False)
	order = models.ForeignKey(Order,on_delete=models.PROTECT, null=False)
	cart_item = models.ForeignKey(Cart_item, on_delete=models.PROTECT, null=False)
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	class Meta:
		abstract = True
		unique_together = ("order_item_id", "order")	
	def __str__(self):
		return str(self.order_id) + str(self.order_item_id)
		
class Order_stock_image(Order_items):
	stock_image = models.ForeignKey('Stock_image', models.CASCADE, null=False)

class Order_user_image(Order_items):
	user_image = models.ForeignKey('User_image', models.CASCADE, null=False)

class Order_stock_collage(Order_items):
	stock_collage = models.ForeignKey('Stock_collage', models.CASCADE, null=False)

class Order_original_art(Order_items):
	original_art = models.ForeignKey('Original_art', models.CASCADE, null=False)


class Order_items_view (models.Model):
	order_item_id = models.AutoField(primary_key=True, null=False)
	order = models.ForeignKey(Order,on_delete=models.PROTECT, null=False)
	cart_item = models.ForeignKey(Cart_item, on_delete=models.PROTECT, null=False)
	product = models.ForeignKey(Product_view, models.PROTECT, null=False)
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False) 	

	class Meta:
		managed = False
		db_table = 'order_items_view'		

	
class Order_shipping (models.Model):
	order_shipping_id = models.AutoField(primary_key=True, null=False)
	store = models.ForeignKey(Ecom_site, models.CASCADE, null=False)
	order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
    )
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
	shipping_address = models.ForeignKey(User_shipping_address, models.PROTECT, null=True) # can be null if user ordering is anonymous
	full_name = models.CharField(max_length=500, blank=False, null=False)
	Company = models.CharField(max_length=600, blank=True, default='')
	address_1 = models.CharField(max_length=600, blank=False, null=False)
	address_2 = models.CharField(max_length=600, blank=True, default='')
	land_mark = models.CharField(max_length=600, blank=True, default='')
	city = models.CharField(max_length=600, blank=False, null=False)
	state = models.ForeignKey(State, on_delete = models.PROTECT, null=True)
	pin_code = models.ForeignKey(Pin_code, on_delete = models.PROTECT, null=True)
	country = models.ForeignKey(Country, on_delete = models.PROTECT, null=False, default= "IND")
	phone_number = models.CharField(max_length=30, blank=True, default='')
	email_id = models.EmailField(blank=True, default='')
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.order) + self.full_name
	
class Order_shipping_status_log (models.Model):
	log_id = models.AutoField(primary_key=True, null=False)
	order = models.ForeignKey(Order, models.PROTECT, null=True)
	order_shipping_status =	models.ForeignKey(Shipping_status, models.PROTECT, null=True)
	status_date = models.DateTimeField(blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.order)
	

class Order_billing (models.Model):
	order_billing_id = models.AutoField(primary_key=True, null=False)
	store = models.ForeignKey(Ecom_site, models.PROTECT)
	order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT
    )
	billing_date =  models.DateField(blank=True, null=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
	billing_address = models.ForeignKey(User_billing_address, models.PROTECT, null=True)
	full_name = models.CharField(max_length=500, blank=False, null=False)
	Company = models.CharField(max_length=600, blank=True, default='')
	address_1 = models.CharField(max_length=600, blank=False, null=False)
	address_2 = models.CharField(max_length=600, blank=True, default='')
	land_mark = models.CharField(max_length=600, blank=True, default='')
	city = models.CharField(max_length=600, blank=False, null=False)
	state = models.ForeignKey(State, on_delete = models.PROTECT, null=True)
	pin_code = models.ForeignKey(Pin_code, on_delete = models.PROTECT, null=True)
	country = models.ForeignKey(Country, on_delete = models.PROTECT, null=False, default= "IND")
	phone_number = models.CharField(max_length=30, blank=True, default='')
	email_id = models.EmailField(blank=True, default='')
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	gst_number = models.CharField(max_length=30, blank=True, default='')

	def __str__(self):
		return str(self.order) + self.full_name

	
############################
#  END:  Business ORDER
############################	
	
	
class Generate_number_by_month(models.Model):
	type = models.CharField(max_length = 50, null=False, primary_key = True)
	description = models.CharField(max_length = 1000, null=True)
	month_year = models.CharField(max_length = 6, null=False)
	current_number = models.IntegerField(null=False)	

class Generate_number(models.Model):
	type = models.CharField(max_length = 50, null=False, primary_key = True)
	description = models.CharField(max_length = 1000, null=True)
	current_number = models.IntegerField(null=False)	


class User_collection(models.Model):
	user_collection_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length=500, blank=False, null =False)
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	
class User_space(models.Model):
	user_space_id = models.AutoField(primary_key=True, null=False)
	user_collection = models.ForeignKey(User_collection, on_delete=models.CASCADE)
	name = models.CharField(max_length=500, blank=False, null =False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


#############################################################################
#  	WISH LIST
############################	
class Wishlist(models.Model):
	wishlist_id = models.AutoField(primary_key=True, null=False)
	store = models.ForeignKey(Ecom_site, models.PROTECT)
	session_id = models.CharField(max_length = 40, blank=True, default='') # to store the session_key in case of anonymous user
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
	voucher = models.ForeignKey(Voucher, models.PROTECT, null=True)
	voucher_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	referral = models.ForeignKey('Referral', on_delete=models.PROTECT, null=True)
	referral_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	quantity = models.IntegerField(null=True)
	wishlist_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	wishlist_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	wishlist_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	wishlist_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	wishlist_status = models.CharField(max_length = 2, blank=True, default='AC') #"AC" Active, "AB":Abandoned, "MV" Moved to cart
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	
class Wishlist_item(models.Model):
	wishlist_item_id = models.AutoField(primary_key=True, null=False) 
	wishlist = models.ForeignKey('Wishlist', models.CASCADE, null=False) 
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	user_collection = models.ForeignKey(User_collection, 
		on_delete=models.CASCADE, null=True)
	user_space = models.ForeignKey(User_space, on_delete=models.CASCADE, 
		null=True)
		

	class Meta:
		abstract = True
		unique_together = ("wishlist_item_id", "wishlist")		

class Wishlist_stock_image(Wishlist_item):
	stock_image = models.ForeignKey('Stock_image', models.CASCADE, null=False)

class Wishlist_user_image(Wishlist_item):
	user_image = models.ForeignKey('User_image', models.CASCADE, null=False)

class Wishlist_stock_collage(Wishlist_item):
	stock_collage = models.ForeignKey('Stock_collage', models.CASCADE, null=False)

class Wishlist_original_art(Wishlist_item):
	original_art = models.ForeignKey('Original_art', models.CASCADE, null=False)

####### A DB View for wishlist_item_view : This will hold all the wishlist items 
class Wishlist_item_view(models.Model):
	wishlist_item_id = models.AutoField(primary_key=True, null=False) 
	wishlist = models.ForeignKey('Wishlist', models.DO_NOTHING, null=False) 
	product = models.ForeignKey(Product_view, models.PROTECT, null=False)
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False)
	user_collection = models.ForeignKey(User_collection, 
		on_delete=models.SET_NULL, null=True)
	user_space = models.ForeignKey(User_space, on_delete=models.SET_NULL, 
		null=True)
	
	class Meta:
		managed = False
		db_table = 'wishlist_item_view'	
############################
#  END:  WISH LIST
############################	

class Stock_image_error(models.Model):
	row_id = models.IntegerField(null=True)
	name = models.CharField(max_length = 128, null=True)
	error = models.CharField(max_length = 2000, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

class Image_url_error(models.Model):
	row_id = models.IntegerField(null=True)
	name = models.CharField(max_length = 128, null=True)
	err_desc = models.CharField(max_length = 2000, null=True)
	error = models.CharField(max_length = 2000, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class Stock_image_category_error(models.Model):
	row_id = models.IntegerField(null=True)
	category_name = models.CharField(max_length = 128, null=True)
	error = models.CharField(max_length = 2000, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	

class Stock_image_stock_image_category_error(models.Model):
	row_id = models.IntegerField(null=True)
	stock_image_category = models.CharField(max_length = 128, null=True)
	error = models.CharField(max_length = 2000, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	
class Publisher_error(models.Model):
	row_id = models.IntegerField(null=True)
	publisher_id = models.CharField(primary_key=True, max_length=10, null=False)
	publisher_name = models.CharField(max_length=256, blank=False,  default='')
	error = models.CharField(max_length = 2000, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

############################
#  Referral
############################	
class Referral(models.Model):
	referred_by = models.ForeignKey(User, on_delete=models.CASCADE,)
	referred_date =  models.DateField(blank=True, null=True)
	name = models.CharField(max_length=150, blank=False, null=False, 
		help_text = "Please enter your friend's Name")
	email_id = models.EmailField(blank=False, null=False, unique=True,
		help_text="Mandatory: Please enter correct email Id", 
		error_messages={'blank':'Email id is required', 'unique':'This email id is already used in a referral'})
	phone_number = models.CharField(max_length=30, blank=True, null=True, 
		help_text = "Optional: Will help us to reach your friend in case of any issues in rewards")
	message = models.CharField(max_length=2000, blank=False, null=False, 
		help_text="Your message will be included in the email we send")
	referred_by_claimed_date = models.DateField(blank=True, null=True)
	referee_claimed_date = models.DateField(blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.referred_by) 	

		
class PrePaymentGateway(models.Model):
	TRN_TYPE = (
		('ORD', 'Order'),
		('EGF', 'Egift'),
	)
	id = models.AutoField(primary_key=True, null=False)
	first_name = models.CharField(max_length=500, blank=True, default='')
	last_name = models.CharField(max_length=500, blank=True, default='')
	phone_number = models.CharField(max_length=30, blank=True, default='')
	email_id = models.EmailField(blank=True, default='')
	rec_id = models.IntegerField(null=False)
	date = models.DateTimeField(blank=True, null=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	trn_type = models.CharField(max_length=3, blank=True, 
		choices=TRN_TYPE, default='ORD')

class Payment_details (models.Model):
	TRN_TYPE = (
		('ORD', 'Order'),
		('EGF', 'Egift'),
	)
	id = models.AutoField(primary_key=True, null=False)
	first_name = models.CharField(max_length=500, blank=True, default='')
	last_name = models.CharField(max_length=500, blank=True, default='')
	phone_number = models.CharField(max_length=30, blank=True, default='')
	email_id = models.EmailField(blank=True, default='')
	rec_id = models.IntegerField(null=False)
	payment_date = models.DateTimeField(blank=True, null=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	payment_txn_status = models.CharField(max_length=10, blank=True, default='')
	payment_txn_id = models.CharField(max_length=250, blank=True, default='')
	payment_txn_amount=models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
	payment_txn_posted_hash=models.CharField(max_length=250, blank=True, default='')
	payment_txn_key=models.CharField(max_length=250, blank=True, default='')
	payment_txn_productinfo=models.CharField(max_length=250, blank=True, default='')
	payment_txn_email=models.CharField(max_length=250, blank=True, default='')
	payment_txn_salt=models.CharField(max_length=250, blank=True, default='')
	payment_firstname = models.CharField(max_length=250, blank=True, default='')
	payment_lastname = models.CharField(max_length=250, blank=True, default='')
	payment_email = models.CharField(max_length=250, blank=True, default='')
	payment_phone = models.CharField(max_length=20, blank=True, default='')
	payment_address1 = models.CharField(max_length=250, blank=True, default='')
	payment_address2 = models.CharField(max_length=250, blank=True, default='')
	payment_city = models.CharField(max_length=250, blank=True, default='')
	payment_state = models.CharField(max_length=250, blank=True, default='')
	payment_country = models.CharField(max_length=250, blank=True, default='')
	payment_zip_code = models.CharField(max_length=20, blank=True, default='')
	cust_email_sent = models.BooleanField(null=False, default=False)
	factory_email_sent = models.BooleanField(null=False, default=False)
	trn_type = models.CharField(max_length=3, blank=True, 
		choices=TRN_TYPE, default='ORD')
	

class Employee(models.Model):
	DEPT_CHOICES = (
		(1, 'Business Support'),
		(2, 'Production'),
		(3, 'Sales'),
		(4, 'Marketting'),
		(5, 'Accounts'),
		(6, 'IT'),
	)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	department = models.PositiveSmallIntegerField(choices=DEPT_CHOICES, null=True)
	is_manager = models.BooleanField('manager status', default=False)
	is_chief = models.BooleanField('chief status', default=False)

	def __str__(self):
		return self.user.username + '(' + str(self.department) + ')'	

class User_sms_email(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
	welcome_email_sent = models.BooleanField(null=False, default=False)
	welcome_sms_sent = models.BooleanField(null=False, default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)
	
	def __str__(self):
		return str(self.user)
	
'''
############################
#  	INVOICE
############################	
class Invoice (models.Model):
	PRINT_STATUS = (
			('N', 'Not printed'),
		('P', 'Printed'),
	)
	invoice_id = models.AutoField(primary_key=True, null=False)
	invoice_number = models.CharField(max_length = 15, blank = True, default = '')
	invoice_date =  models.DateField(blank=True, null=True)
	order = models.ForeignKey(Order,on_delete=models.PROTECT, null=False)
	store = models.ForeignKey(Ecom_site, models.PROTECT)
	session_id = models.CharField(max_length = 40, blank=True, default='') # to store the session_key in case of anonymous user
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
	voucher = models.ForeignKey(Voucher, models.PROTECT, null=True)
	voucher_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	referral = models.ForeignKey('Referral', on_delete=models.PROTECT, null=True)
	referral_disc_amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	unit_price = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	quantity = models.IntegerField(null=True)
	sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	order_discount_amt = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	tax = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	invoice_total = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	shipping_method = models.ForeignKey(Shipping_method, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup
	shipper = models.ForeignKey(Shipper, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup	
	shipping_status = models. ForeignKey(Shipping_status, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup
	print_status = models.CharField(max_length = 1, blank=True, 
		choices=PRINT_STATUS, default='PP') 
	cust_email_sent = models.BooleanField(null=False, default=False) 
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.invoice_id) + ' - ' + str(self.user)


class Invoice_items (models.Model):
	invoice_item_id = models.AutoField(primary_key=True, null=False)
	invoice = models.ForeignKey(Invoice,on_delete=models.PROTECT, null=False)
	cart_item = models.ForeignKey(Cart_item, on_delete=models.PROTECT, null=False)
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	class Meta:
		abstract = True
		unique_together = ("invoice_item_id", "invoice")	
	def __str__(self):
		return str(self.invoice_id) + str(self.invoice_item_id)
		
class Invoice_stock_image(Invoice_items):
	stock_image = models.ForeignKey('Stock_image', models.CASCADE, null=False)

class Invoice_user_image(Invoice_items):
	user_image = models.ForeignKey('User_image', models.CASCADE, null=False)

class Invoice_stock_collage(Invoice_items):
	stock_collage = models.ForeignKey('Stock_collage', models.CASCADE, null=False)

class Invoice_original_art(Invoice_items):
	original_art = models.ForeignKey('Original_art', models.CASCADE, null=False)


class Invoice_items_view (models.Model):
	invoice_item_id = models.AutoField(primary_key=True, null=False)
	invoice = models.ForeignKey(Invoice,on_delete=models.PROTECT, null=False)
	cart_item = models.ForeignKey(Cart_item, on_delete=models.PROTECT, null=False)
	product = models.ForeignKey(Product_view, models.PROTECT, null=False)
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False) 	

	class Meta:
		managed = False
		db_table = 'invoice_items_view'		
'''

class Homelane_data(models.Model):
	homelane_key =  models.AutoField(primary_key=True)
	product = models.ForeignKey(Stock_image, on_delete=models.CASCADE, null=False)
	product_name = models.CharField(max_length = 128, null=True, default = '')
	description = models.CharField(max_length = 2000, blank=True, default = '')
	part_number = models.CharField(max_length = 30, null=True)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	category = models.ForeignKey(Stock_image_category, models.CASCADE, null=True)
	category_name = models.CharField(max_length = 128, null=True, default = '')
	is_published = models.BooleanField(null=False, default=False)
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
	framed_url = models.CharField(max_length = 1000, blank=True, default='')
	framed_thumbnail_url = models.CharField(max_length = 1000, blank=True, default='')
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	promotion_name = models.CharField(max_length = 128, null=True, default = '')
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_name = models.CharField(max_length = 30, null=True, default = '')
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_name = models.CharField(max_length = 30, null=True, default = '')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_name = models.CharField(max_length = 30, null=True, default = '')
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_name = models.CharField(max_length = 30, null=True, default = '')
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_name = models.CharField(max_length = 30, null=True, default = '')
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_name = models.CharField(max_length = 30, null=True, default = '')
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	ordered = models.BooleanField(null=False, default=False)
	order_number = models.CharField(max_length = 15, blank = True, default = '')
	order_date = models.DateField(blank=True, null=True)
	
	def __str__(self):
		return str( self.product_id ) + " " + self.product_name



class Amazon_data(models.Model):
	PARENT_CHILD = (
		('P', 'Parent'),
		('C', 'Child'),
	)


	amazon_key =  models.AutoField(primary_key=True)
	amazon_sku =  models.CharField(max_length = 15, null=True, default = '')
	product = models.ForeignKey(Stock_image, on_delete=models.CASCADE, null=False)
	product_name = models.CharField(max_length = 128, null=True, default = '')
	description = models.CharField(max_length = 2000, blank=True, default = '')
	part_number = models.CharField(max_length = 30, null=True)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	category = models.ForeignKey(Stock_image_category, models.CASCADE, null=True)
	category_name = models.CharField(max_length = 128, null=True, default = '')
	is_published = models.BooleanField(null=False, default=False)
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
	framed_url = models.CharField(max_length = 1000, blank=True, default='')
	framed_thumbnail_url = models.CharField(max_length = 1000, blank=True, default='')
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	promotion_name = models.CharField(max_length = 128, null=True, default = '')
	quantity = models.IntegerField(null=True)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=True)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=True)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	item_total = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_name = models.CharField(max_length = 30, null=True, default = '')
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_name = models.CharField(max_length = 30, null=True, default = '')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_name = models.CharField(max_length = 30, null=True, default = '')
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_name = models.CharField(max_length = 30, null=True, default = '')
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_name = models.CharField(max_length = 30, null=True, default = '')
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_name = models.CharField(max_length = 30, null=True, default = '')
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	ordered = models.BooleanField(null=False, default=False)
	order_number = models.CharField(max_length = 15, blank = True, default = '')
	order_date = models.DateField(blank=True, null=True)
	parent_child = models.CharField(max_length = 1, null=True, default = 'P',
		choices = PARENT_CHILD)
	parent_amz_sku = models.CharField(max_length = 15, null=True, default = '')
	
	def __str__(self):
		return str( self.product_id ) + " " + self.product_name


class Newsletter_subscription(models.Model):
	email = models.EmailField(null=False)
	subscription_active = models.BooleanField(null=False, default=False)
	subscription_start_date = models.DateField(blank=True, null=True)
	subscription_end_date = models.DateField(blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class User_ip_address(models.Model):
	session_id = models.CharField(max_length = 40, blank=True, default='') # to store the session_key in case of anonymous user
	userlogged_in = models.BooleanField(null=False, default=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	site_visit_datetime = models.DateTimeField(auto_now_add=True, null=False)
	ip_address = models.CharField(max_length = 50, blank=True, default = '')


'''
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
	artist_id = models.CharField(primary_key=True, max_length=10, null=False)
	first_name = models.CharField(max_length=256, blank=False,  default='')
	last_name = models.CharField(max_length=256, blank=False,  default='')
	artist_group = models.ForeignKey(Artist_group, models.SET_NULL, null=True)
	artist_profile = models.CharField(max_length=2000, blank=False, default='')
	publisher = models.ForeignKey(Publisher, models.CASCADE, null=True)
	store = models.ForeignKey(Ecom_site, models.CASCADE, null=False)
	gallary_url = models.CharField(max_length = 1000, blank=True, default='')
	default_original_art_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	
	def __str__(self):
		return self.first_name + " " + self.last_name

class Artist_art (models.Model):
	ART_TYPE = (
		('PAINTING', 'Painting'),
		('PHOTOGRAPH', 'Photograph'),
		('SKETCH', 'Sketch'),
	)
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
	product = models.ForeignKey(Product_view, models.PROTECT, null=False)
	product_type = models.ForeignKey(Product_type, null=True, on_delete=models.SET_NULL)
	art_print_allowed = models.BooleanField(null=False, default=False)
	original_art_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	available_qty = models.IntegerField(null=False)	
	sold_qty = models.IntegerField(null=True)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return self.artist + str(self.product)

class Inventory_udate(models.Model):
	product = models.ForeignKey(Product_view, models.PROTECT, null=False)
	product_type = models.ForeignKey(Product_type, null=True, on_delete=models.SET_NULL)
	update_qty = models.IntegerField(null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.product) + str(updated_qty)
	
'''
		
@receiver(post_save, sender=User_image, dispatch_uid="update_image_profile")
def update_image(sender, instance, **kwargs):
	if instance.image_to_frame:
	#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	#fullpath = BASE_DIR + instance.image_to_frame.url
		fullpath = settings.PROJECT_DIR + instance.image_to_frame.url
		rotate_image(fullpath)

	
def rotate_image(filepath):
	try:
		image = Image.open(filepath)
		for orientation in ExifTags.TAGS.keys():
			if ExifTags.TAGS[orientation] == 'Orientation':
				break
		exif = dict(image._getexif().items())

		if exif[orientation] == 3:
			image = image.rotate(180, expand=True)
		elif exif[orientation] == 6:
			image = image.rotate(270, expand=True)
		elif exif[orientation] == 8:
			image = image.rotate(90, expand=True)
		image.save(filepath)
		image.close()
	except (AttributeError, KeyError, IndexError):
		# cases: image don't have getexif
		pass

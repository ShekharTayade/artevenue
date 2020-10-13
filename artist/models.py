from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.fields import DecimalField

from artevenue.models import Ecom_site, Product_type, Original_art, Order_items_view, Product_view, Order


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
	profile_name = models.CharField(max_length=200, blank=False, default='') ## use for display (ex. Jaideep Kumar)
	url_name = models.CharField(max_length=50, blank=False, default='')  ## used for creating url (ex. 'jaideep_kumar' in https://www.artevenue.com/artist/jaideep_kumar)
	profile_photo = models.ImageField(upload_to='artist/profile_photo/%Y/%m/%d/', blank=True, default="")
	profile_tagline = models.CharField(max_length=500, blank=False, default='')
	publisher = models.ForeignKey('artevenue.Publisher', models.CASCADE, null=True)
	store = models.ForeignKey('artevenue.Ecom_site', models.CASCADE, null=False)
	gallary_url = models.CharField(max_length = 1000, blank=True, default='')
	default_original_art_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	approved = models.BooleanField(null=False, default=False)
	approval_date =  models.DateTimeField(blank=True, null=True)
	
	def __str__(self):
		return self.first_name + " " + self.last_name

	def save(self, *args, **kwargs):
		if self.profile_photo:
			self.create_thumbnail()
			
		super(Artist, self).save()	

	def create_thumbnail(self):
		from PIL import Image, ExifTags
		from io import BytesIO
		import os
		# If there is no image associated with this.
		# do not create thumbnail
		if not self.profile_photo:
			return

		# Set our max thumbnail size in a tuple (max width, max height)
		THUMBNAIL_SIZE = (200,200)
		PIL_TYPE = ''
		if self.profile_photo.name.lower().endswith(".jpg"):
			PIL_TYPE = 'jpeg'
			FILE_EXTENSION = 'jpg'
			DJANGO_TYPE = 'image/jpeg'
		if self.profile_photo.name.lower().endswith(".png"):
			PIL_TYPE = 'png'
			FILE_EXTENSION = 'png'
			DJANGO_TYPE = 'image/png'
		if self.profile_photo.name.lower().endswith(".gif"):
			PIL_TYPE = 'gif'
			FILE_EXTENSION = 'gif'
			DJANGO_TYPE = 'image/gif'
		if PIL_TYPE == '' :
			extension = os.path.splitext(self.profile_photo.name)[1]
			PIL_TYPE = extension.lower()[1:]
			FILE_EXTENSION = PIL_TYPE
			DJANGO_TYPE = 'image/' + PIL_TYPE[1:]

		# Open original photo which we want to thumbnail using PIL's Image
		image = Image.open(self.profile_photo)
			
		# use our PIL Image object to create the thumbnail, which already
		image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

		# Save the thumbnail
		temp_handle = BytesIO()		
		image.save(temp_handle, PIL_TYPE)
		temp_handle.seek(0)
		
		# Save image to a SimpleUploadedFile which can be saved into ImageField
		from django.core.files.uploadedfile import SimpleUploadedFile
		suf = SimpleUploadedFile(os.path.split(self.profile_photo.name)[-1],
								 temp_handle.read(), content_type=DJANGO_TYPE)
		# Save SimpleUploadedFile into image field
		self.profile_photo.save(
			'%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
			suf, save=False)



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
	artist_listed = models.BooleanField(null=False, default=False)
	approved = models.BooleanField(null=False, default=False)
	approval_date = models.DateTimeField(null = True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	unapproved = models.BooleanField(null=False, default=False)
	unapproval_date = models.DateTimeField(null = True)


class Artist_original_art (models.Model):
	SELL_MODE = (
		('O', 'ONLY ORIGINAL'),
		('A', 'ONLY ART PRINT'),
		('B', 'BOTH'),
	)
	REASON =  (
		('I', 'Artwork image is not fit for listing, Please upload another image. Follow image guidelines.'),
		('X', 'Artwork not found fit for listing'),
		('O', 'Other reason (Please get in touch with us)'),
	)
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
	product = models.ForeignKey('artevenue.Original_art', models.PROTECT, null=False)
	sell_mode = models.CharField(max_length=1, choices = SELL_MODE, null=True)
	artist_listed = models.BooleanField(null=False, default=False)
	uploaded_date = models.DateField(null = True)
	approved = models.BooleanField(null=False, default=False)
	approval_date = models.DateTimeField(null = True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	unapproved = models.BooleanField(null=False, default=False)
	unapproval_date = models.DateTimeField(null = True)
	unapproval_reason = models.CharField(max_length=1, choices = REASON, null=False, default = '')
	artist_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)


class Inventory_udate(models.Model):
	product = models.ForeignKey(Original_art, models.PROTECT, null=False)
	product_type = models.ForeignKey('artevenue.Product_type', null=True, on_delete=models.SET_NULL)
	update_qty = models.IntegerField(null=False)	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	

	def __str__(self):
		return str(self.product) + str(updated_qty)

class Generate_art_number(models.Model):
	NUM_TYPE = (
		('PART', 'Part Number'),
		('ORIG', 'Original ID'),
		('STKI', 'Stock Image ID'),
	)

	publisher = models.CharField(max_length = 20, null=False)
	type = models.CharField(max_length = 4, choices = NUM_TYPE, null=False)
	prefix = models.CharField(max_length = 10, null=False) 
	suffix = models.CharField(max_length = 10, null=False, default = '')
	current_number = models.IntegerField(null=False)	

	def __str__(self):
		return self.type + ", " + self.publisher + ', ' + self.prefix + str(current_number) + ', ' + self.suffix


class Artist_sales(models.Model):
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE) 
	product_id = models.IntegerField(null=False, default = 0)		## USE THIS TO REFER TO PRODUCT_VIEW ALONG WITH PRODUCT_TYPE
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	part_number = models.CharField(max_length = 30, null=True)
	order = models.ForeignKey(Order, models.PROTECT, null=False)
	order_item_id = models.IntegerField(null=False, default = 0) ## USE THIS TO REFER TO ORDER_ITEMS_VIEW
	sale_value = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	license_fee = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	pay_date = models.DateField(null = True)
	pay_reference = models.CharField(max_length = 100, null=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	
	
	
	def __str__(self):
		return self.artist + " - " + self.part_number + " - " + str(sale_value)
		
		
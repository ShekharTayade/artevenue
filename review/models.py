from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from artevenue.models import Stock_image, Order, Product_type, Country

class Customer_review_stock_image( models.Model):
	REVIEW_RATING = (
		('1', 'Not Worth'),
		('2', 'Can be Better'),
		('3', 'As Expected'),
		('4', 'Satisfied'),
		('5', 'Highly Satisfied'),
	)	
	review_id = models.AutoField(primary_key=True)
	featured = models.BooleanField(null=False, default=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
	name = models.CharField(max_length=500, blank=False, default='')
	email_id = models.EmailField(blank=True, default='')
	phone_number = models.CharField(max_length=30, blank=True, default='')	
	location = models.CharField(max_length=500, blank=False, default='')
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
	product = models.ForeignKey(Stock_image, models.PROTECT, null=True)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	rating =  models.DecimalField(max_digits=3, decimal_places=2, null=True)
	headline = models.CharField(max_length=100, blank=False, default='')
	comments = models.CharField(max_length=2000, blank=False, default='')
	posted_date = models.DateTimeField(auto_now_add=True, null=False)
	approved_date = models.DateTimeField(null=True)
	order_id = models.ForeignKey(Order, on_delete=models.CASCADE, null = True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)
	updated_date = models.DateTimeField(auto_now_add=True, null=False)

class  Customer_review_stock_image_pics( models.Model):
	pic_id = models.AutoField(primary_key=True)	
	customer_review_stock_image = models.ForeignKey(Customer_review_stock_image, 
		on_delete=models.CASCADE, null=False)
	photo = models.ImageField(upload_to='user_photos/%Y/%m/%d/', blank=True, default="")
	user_photo_thumbnail = models.ImageField(upload_to='user_photos/%Y/%m/%d/', blank=True, default="")
	def create_thumbnail(self):
		# If there is no image associated with this.
		# do not create thumbnail
		if not self.photo:
			return

		# Set our max thumbnail size in a tuple (max width, max height)
		THUMBNAIL_SIZE = (75, 75)
		PIL_TYPE = ''
		if self.photo.name.lower().endswith(".jpg"):
			PIL_TYPE = 'jpeg'
			FILE_EXTENSION = 'jpg'
			DJANGO_TYPE = 'image/jpeg'
		if self.photo.name.lower().endswith(".png"):
			PIL_TYPE = 'png'
			FILE_EXTENSION = 'png'
			DJANGO_TYPE = 'image/png'
		if self.photo.name.lower().endswith(".gif"):
			PIL_TYPE = 'gif'
			FILE_EXTENSION = 'gif'
			DJANGO_TYPE = 'image/gif'
		if PIL_TYPE == '' :
			extension = os.path.splitext(self.photo.name)[1]
			PIL_TYPE = extension.lower()[1:]
			FILE_EXTENSION = PIL_TYPE
			DJANGO_TYPE = 'image/' + PIL_TYPE[1:]

		# Open original photo which we want to thumbnail using PIL's Image
		image = Image.open(self.photo)

		# use our PIL Image object to create the thumbnail, which already
		image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

		# Save the thumbnail
		#temp_handle = StringIO()
		temp_handle = BytesIO()
		image.save(temp_handle, PIL_TYPE)
		temp_handle.seek(0)
		
		# Save image to a SimpleUploadedFile which can be saved into ImageField
		from django.core.files.uploadedfile import SimpleUploadedFile
		suf = SimpleUploadedFile(os.path.split(self.photo.name)[-1],
								 temp_handle.read(), content_type=DJANGO_TYPE)
		# Save SimpleUploadedFile into image field
		self.photo_thumbnail.save(
			'%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
			suf, save=False)

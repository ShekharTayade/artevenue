from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from artevenue.models import Stock_image, Product_view, Order

class Customer_reviews( models.Model):
	REVIEW_RATING = (
		('1', 'Not Worth'),
		('2', 'Can be Better'),
		('3', 'As Expected'),
		('4', 'Satisfied'),
		('5', 'Highly Satisfied'),
	)	
	review_id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
	name = models.CharField(max_length=500, blank=False, default='')
	product = models.ForeignKey(Product_view, models.PROTECT, null=True)
	product_type = models.ForeignKey(Product_type, models.CASCADE, null=True)
	rating = models.CharField(max_length=1, blank=False, default='')
	likes = models.CharField(max_length=500, blank=False, default='')
	review = models.CharField(max_length=2000, blank=False, default='')
	posted_date = models.DateTimeField(auto_now_add=True, null=False)
	approved_date = models.DateTimeField(null=True)
	order_id = models.ForeignKey(Order, on_delete=models.CASCADE, null = True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)
	updated_date = models.DateTimeField(auto_now_add=True, null=False)
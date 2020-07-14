from django import template

from django.shortcuts import render, get_object_or_404
from datetime import datetime
import datetime
from django.db import IntegrityError, DatabaseError, Error

from review.models import Customer_review_stock_image, Customer_review_stock_image_pics
from artevenue.models import Ecom_site, Product_view

from django.http import HttpResponse
from django.conf import settings
from django.db.models import Avg, Count

today = datetime.date.today()

register = template.Library()

@register.inclusion_tag('review/customer_review.html')
def customer_review(product_id=None, cart_item_id=None, wishlist_item_id=None, user_width=None, user_height=None):
	overall_rating = None
	total_reviews = None

	if user_width == '0':
		user_width = None
	if user_height == '0':
		user_height = None
	
	avg_rating = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False).aggregate(avg_rating=Avg('rating'))
	rating_cnt = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False).aggregate(rating_cnt=Count('rating'))
	
	if avg_rating:
		overall_rating = round(avg_rating['avg_rating'],2)
	else: 
		overall_rating = None
	'''
	if rt:
		if  rt > 0 and rt <= 0.5:
			overall_rating = 0.5
		elif rt > 0.5 and rt <= 1:
			overall_rating = 1
		elif rt > 1 and rt <= 1.5:
			overall_rating = 1.5
		elif rt > 1.5 and rt <= 2:
			overall_rating = 2
		elif rt > 2 and rt <= 2.5:
			overall_rating = 2.5
		elif rt > 2.5 and rt <= 3:
			overall_rating = 3
		elif rt > 3 and rt <= 3.5:
			overall_rating = 3.5
		elif rt > 3.5 and rt <= 4:
			overall_rating = 4
		elif rt > 4 and rt <= 4.5:
			overall_rating = 4.5
		elif rt > 4.5:
			overall_rating = 5
	'''
	if rating_cnt:
		total_reviews = rating_cnt['rating_cnt']
	
	reviews = Customer_review_stock_image.objects.filter(featured = True,
		approved_date__isnull = False)[:4]

	review_pics = Customer_review_stock_image_pics.objects.filter(
			customer_review_stock_image__in = reviews )

	
	return { 'overall_rating':overall_rating, 'total_reviews':total_reviews,
		'reviews' : reviews, 'product_id': product_id, 'cart_item_id':cart_item_id, 
		'wishlist_item_id':wishlist_item_id, 'user_width':user_width, 
		'user_height':user_height, 'review_pics':review_pics}


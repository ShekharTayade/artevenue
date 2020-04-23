from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
from django.http import JsonResponse
from django.db.models import Avg, Count

from artevenue.models import Country, State, Ecom_site, Stock_image, Order, Order_items_view
from artevenue.models import UserProfile

from review.models import Customer_review_stock_image

from review.forms import CustomerReviewForm

from django.contrib import messages
import datetime

ecom = Ecom_site.objects.get(pk=settings.STORE_ID)

@login_required
def write_customer_review(request, prod_id = None, prod_type = None):
	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
		customer_review_form = CustomerReviewForm(initial={'name': user.username,})
		
		## Get the products in orders
		order_items = Order_items_view.objects.filter(order__user = user,
			product__product_type_id = F('product_type_id') ).exclude(
			order__order_status = 'PP').select_related('product')
			
		if prod_id and prod_type:
			order_items = order_items.filter(product_id = prod_id, product_type_id = prod_type)
	else:
		msg = "To write a review, you need to be logged in and have ordered from artevenue.com."
		customer_review_form = None
		order_items = None
	return render(request, "review/write_customer_review.html", 
		{'customer_review_form':customer_review_form, 'order_items':order_items})
		

@login_required
def upload_photo(request):

	return JsonResponse({'status_code':'200'})
	'''
	if request.user.is_authenticated:
		if review_id:
			rev = Customer_review_stock_image.obejcts.get(review_id = review_id)
		else:
			rev = Customer_review_stock_image()
			rev.user = ''
			rev.name = ''
			rev.email_id = ''
	'''	

def customer_review_one(request, review_id):

	product_id = request.POST.get("product_id", None)
	cart_item_id = request.POST.get("cart_item_id", None)
	wishlist_item_id = request.POST.get("wishlist_item_id", None)
	user_width = request.POST.get("user_width", None)
	user_height = request.POST.get("user_height", None)

	review = Customer_review_stock_image.objects.get(review_id = review_id,
		approved_date__isnull = False)

	return render( request, "review/customer_review_one.html", {'review':review,
		'product_id': product_id, 'cart_item_id':cart_item_id, 
		'wishlist_item_id':wishlist_item_id, 'user_width':user_width, 
		'user_height':user_height} )

	
def all_customer_reviews(request):

	product_id = request.POST.get("product_id", None)
	cart_item_id = request.POST.get("cart_item_id", None)
	wishlist_item_id = request.POST.get("wishlist_item_id", None)
	user_width = request.POST.get("user_width", None)
	user_height = request.POST.get("user_height", None)
	

	overall_rating = None
	total_reviews = None

	
	avg_rating = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False).aggregate(avg_rating=Avg('rating'))
	rating_cnt = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False).aggregate(rating_cnt=Count('rating'))
	
	if avg_rating:
		overall_rating = round(avg_rating['avg_rating'],2)
	else: 
		overall_rating = None
	
	if rating_cnt:
		total_reviews = rating_cnt['rating_cnt']
	
	reviews = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False).order_by('-updated_date')

	return render( request, "review/customer_reviews_all.html", {'reviews':reviews,
		'total_reviews':total_reviews, 'overall_rating':overall_rating,
		'product_id': product_id, 'cart_item_id':cart_item_id, 
		'wishlist_item_id':wishlist_item_id, 'user_width':user_width, 
		'user_height':user_height} )

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
from django.http import HttpResponse
from django.conf import settings

from artevenue.models import Country, State, Ecom_site, Stock_image, Order, Order_items_view
from artevenue.models import UserProfile, Order_stock_image, Order_billing

from review.models import Customer_review_stock_image, Customer_review_stock_image_pics, Customer_review_stock_image_order_item

from review.forms import CustomerReviewForm

from django.contrib import messages
import datetime

import urllib
import json
import os
import re
from PIL import Image, ExifTags


ecom = Ecom_site.objects.get(pk=settings.STORE_ID)
env = settings.EXEC_ENV

def write_customer_review(request, order_id = None, prod_id = None, prod_type = None):
	env = settings.EXEC_ENV
	status = "SUCCESS"
	msg = None
	today = datetime.datetime.today()
	dt = today.date()
	s_dt = dt + datetime.timedelta(days=-180)
	
	if request.user:
		try:
			user = User.objects.get(username = request.user)
		except User.DoesNotExist:
			user = None
	else:
		user = None
	
	if request.method == 'POST':
		rating = request.POST.get('rating', '')
		name = request.POST.get('name', '')
		email_id = request.POST.get('email_id', '')
		phone_number = request.POST.get('phone_number', '')
		location = request.POST.get('location', '')
		country = request.POST.get('country', '')
		headline = request.POST.get('headline', '')
		comments = request.POST.get('comments', '')
		use = request.POST.get('allow_to_use', 'FALSE')
		if use == 'TRUE':
			allow_to_use = True
		else:
			allow_to_use = False
		file1 = request.FILES.get('user_photo1', None)
		file2 = request.FILES.get('user_photo2', None)
		file3 = request.FILES.get('user_photo3', None)
		file4 = request.FILES.get('user_photo4', None)
		file5 = request.FILES.get('user_photo5', None)
		file6 = request.FILES.get('user_photo6', None)
		file7 = request.FILES.get('user_photo7', None)
		file8 = request.FILES.get('user_photo8', None)

		ord_itms_list = request.POST.get('selected_prods', '')
		ord_itms = ord_itms_list.split(",")

		if rating == '' or rating == 'None' :
			status = 'FAILURE'
			msg = 'Please choose your rating by clicking on stars'
		if headline == '':
			status = 'FAILURE'
			msg = 'Please enter a headline your review.'
		if comments == '':
			status = 'FAILURE'
			msg = 'Please enter your feedback. It will help us feel proud or do better.'

		if phone_number != '' and phone_number is not None:
			regex = r'^[6-9]\d{9}$'
			isValid = re.match(regex, phone_number)		  
			if not isValid:
				msg = "Please enter 10-digit mobile number without prefix +91 or 0. You can leave it blank if you don't want to share your phone number."
				status = 'FAILURE'

		# get the token submitted in the form
		recaptcha_response = request.POST.get('g-recaptcha-response')
		url = 'https://www.google.com/recaptcha/api/siteverify'
		payload = {
			'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
			'response': recaptcha_response
		}
		data = urllib.parse.urlencode(payload).encode()
		req = urllib.request.Request(url, data=data)

		# verify the token submitted with the form is valid
		response = urllib.request.urlopen(req)
		result = json.loads(response.read().decode())

		# result will be a dict containing 'success' and 'action'.
		# it is important to verify both
		if (not result['success']) or (not result['action'] == 'write_review'):
			msg = 'To prevent spaming, we request you to navigate to some other page and come back to this page(Invalid reCAPTCHA).'
			status = "FAILURE"
			
			
		if status == 'SUCCESS':

			#Update review
			try:
				cnty = Country.objects.get(country_name__iexact = country.upper())
				
				rev = Customer_review_stock_image.objects.create(
					featured = False,
					user = user,
					name = name,
					email_id = email_id,
					phone_number = phone_number,	
					location = location,
					country = cnty,
					product = None,
					product_type = None,
					rating =  rating,
					headline = headline,
					comments = comments,
					posted_date = today,
					approved_date = None,
					allow_to_use = allow_to_use,
					order_id = None,
					created_date = today,
					updated_date = today
				)
			
				#rev.save()
			except IntegrityError as e:
				status = 'FAILURE'
				msg = 'We seem to be having some system issue at the moment. We appreciate if you let us know of this using Contact Us link at the in the footer.'
				customer_review_form = CustomerReviewForm(
					initial = ({'rating': rating, 'name' : user.username,
								headline: 'headline', 'comments': comments,}
								)
				)	
			
			## Save the user photos		
			if file1:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file1,
					disp_seq = None
					)
				p.save()
			if file2:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file2,
					disp_seq = None
					)
				p.save()
			if file3:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file3,
					disp_seq = None
					)
				p.save()
			if file4:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file4,
					disp_seq = None
					)
				p.save()
			if file5:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file5,
					disp_seq = None
					)
				p.save()
			if file6:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file6,
					disp_seq = None
					)
				p.save()
			if file7:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file7,
					disp_seq = None
					)
				p.save()
			if file8:
				p = Customer_review_stock_image_pics(
					customer_review_stock_image = rev,
					photo = file8,
					disp_seq = None
					)
				p.save()
				
			## Save products
			if ord_itms:
				for p in ord_itms:
					if p != None and p != '':
						pr = Order_stock_image.objects.filter(order_item_id = p).first()
						if pr is not None:
							i = Customer_review_stock_image_order_item(
								customer_review_stock_image = rev,
								order_stock_image = pr
								)
							i.save()					
							
			customer_review_form = CustomerReviewForm(
				initial = ({'rating': rating, 'name' : name,
						'headline': headline, 'comments': comments,
						'location': location, 'country':country,
						'allow_to_use': allow_to_use, 'email_id': email_id,
						'phone_number': phone_number
						}
				)
			)

			## Confirmation
			return render(request, "review/customer_review_confirmation.html", 
				{'customer_review_form':customer_review_form,
				'status': status, 'msg':msg, 'env': env})
		
		else:

			customer_review_form = CustomerReviewForm(
				initial = ({'rating': rating, 'name' : name,
							'headline': headline, 'comments': comments,
							'location': location, 'country':country,
							'allow_to_use': allow_to_use, 'email_id': email_id,
							'phone_number': phone_number
							}
				)
			)
		
	else:
		if user:			
			ords = Order_billing.objects.filter(order__user = user).last()			
			if ords:
				location = ords.city
				country = ords.country.country_name
				phone_number = ords.phone_number
				customer_review_form = CustomerReviewForm(initial={'name': user.username,
					'email_id': user.email, 'location': location, 'country': country,
					'phone_number': phone_number})
			else:				
				customer_review_form = CustomerReviewForm(initial={'name': user.username,
					'email_id': user.email})
		else:
			customer_review_form = CustomerReviewForm()
			
	## Get the products in orders
	if user:
		order_items = Order_items_view.objects.filter(order__user = user,
			order__order_date__gte = s_dt,
			product__product_type_id = F('product_type_id') ).exclude(
			order__order_status = 'PP').select_related('product')
	else:
		order_items = None
	
	return render(request, "review/write_customer_review.html", 
		{'customer_review_form':customer_review_form, 'order_items':order_items,
		'status': status, 'msg':msg, 'env': env})

def customer_review_one(request, review_id):

	product_id = request.POST.get("product_id", None)
	cart_item_id = request.POST.get("cart_item_id", None)
	wishlist_item_id = request.POST.get("wishlist_item_id", None)
	user_width = request.POST.get("user_width", None)
	user_height = request.POST.get("user_height", None)

	review = Customer_review_stock_image.objects.get(review_id = review_id,
		approved_date__isnull = False)

	review_pics = Customer_review_stock_image_pics.objects.filter(
			customer_review_stock_image = review )


	return render( request, "review/customer_review_one.html", {'review':review,
		'product_id': product_id, 'cart_item_id':cart_item_id, 
		'wishlist_item_id':wishlist_item_id, 'user_width':user_width, 
		'user_height':user_height, 'review_pics': review_pics} )

	
def all_customer_reviews(request, page=None, stars=0):

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
		
	reviews_all = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False).order_by('-updated_date')
	
	star1_cnt = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False, rating = 1).count()
	star2_cnt = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False, rating = 2).count()
	star3_cnt = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False, rating = 3).count()
	star4_cnt = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False, rating = 4).count()
	star5_cnt = Customer_review_stock_image.objects.filter(
		approved_date__isnull = False, rating = 5).count()
	
	star = request.GET.get('star', 0)
	starcnt = 0
	if star != 0:
		reviews_all = reviews_all.filter(rating = star)
		starcnt = reviews_all.count()


	if not page:
		page = request.GET.get('page', 1)
	paginator = Paginator(reviews_all, 15) 
	
	try:
		reviews = paginator.page(page)	
	except PageNotAnInteger:
		reviews = paginator.page(1)
	except EmptyPage:
		reviews = paginator.page(paginator.num_pages)
		
	#reviews = paginator.get_page(page)		


	review_pics = Customer_review_stock_image_pics.objects.filter(
			customer_review_stock_image__in = reviews )

	review_pics_all = Customer_review_stock_image_pics.objects.all().order_by('disp_seq')[:20]

	return render( request, "review/customer_reviews_all.html", {'reviews':reviews,
		'total_reviews':total_reviews, 'overall_rating':overall_rating,
		'product_id': product_id, 'cart_item_id':cart_item_id, 
		'wishlist_item_id':wishlist_item_id, 'user_width':user_width, 
		'user_height':user_height, 'review_pics':review_pics, 'star': star,
		'starcnt': starcnt, 'star1_cnt':star1_cnt, 'star2_cnt' :star2_cnt,
		'star3_cnt':star3_cnt, 'star4_cnt':star4_cnt, 'star5_cnt': star5_cnt,
		'review_pics_all': review_pics_all } )

def get_customer_review_image(request):
		
		pic_id = request.GET.get('pic_id','')
		
		try:
			pic = Customer_review_stock_image_pics.objects.get(pic_id = pic_id)

			from PIL import Image
			from io import BytesIO
			import base64

			# Read the image
			im=Image.open(pic.photo)
			
			buffered = BytesIO()
			im.save(buffered, format='JPEG')
			img_data = buffered.getvalue()
			img_str = base64.b64encode(img_data)
						
			return HttpResponse(img_str)
		except Customer_review_stock_image_pics.DoesNotExist:
			pic = {}
			return HttpResponse('')

		
def customer_photos_all(request, page=None):

	pics = Customer_review_stock_image_pics.objects.all().order_by('disp_seq')

	if not page:
		page = request.GET.get('page', 1)
	paginator = Paginator(pics, 50) 
	
	try:
		review_pics = paginator.page(page)	
	except PageNotAnInteger:
		review_pics = paginator.page(1)
	except EmptyPage:
		review_pics = paginator.page(paginator.num_pages)
	
	return render( request, "review/customer_photos_all.html",
		{'review_pics':review_pics} )

def fix_orientation(img):
	for orientation in ExifTags.TAGS.keys():
		if ExifTags.TAGS[orientation] == 'Orientation':
			break
	exif = dict(img._getexif().items())

	if exif[orientation] == 3:
		img = img.rotate(180, expand=True)
	elif exif[orientation] == 6:
		img = img.rotate(270, expand=True)
	elif exif[orientation] == 8:
		img = img.rotate(90, expand=True)
	return img
	
	
def save_photos(rev, file):
	'''
	if env == 'DEV' or env == 'TESTING':
		path = settings.BASE_DIR + "/media/user_photos/all/"
	else:
		path = settings.PROJECT_DIR + "/media/user_photos/all/"
		
	f = Image.open(file)
	img = fix_orientation(f)
	ratio =  img.width / img.height
	img = img.resize((900, int(900/ratio)))
	img.save(path + file.name, "JPEG")
	'''
	## Thumbnail
	#thumb_file_nm, ext = os.path.splitext(file.name)
	#thumb_img = img.resize((150, int(150/ratio)))
	#thumb_img.save(path + thumb_file_nm + "_thumbnail.jpeg", "JPEG")
	#Created automatically in models.py

	#Update in database

	return
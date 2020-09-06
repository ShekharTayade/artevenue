from django.shortcuts import render, get_object_or_404
from datetime import datetime
import datetime
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Count, Q, Max, Sum

from django.shortcuts import render,redirect
from django.contrib import messages

from artevenue.models import Ecom_site, Cart
from artevenue.forms import contactUsForm, referralForm, egiftForm

from artevenue.models import Pin_code, City, State, Country, Pin_city_state_country, Newsletter_subscription
from artevenue.models import Referral, Egift_card_design, Egift, Voucher, Voucher_user, User_ip_address
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from PIL import ImageFont, ImageDraw
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.template.loader import render_to_string
from django.utils.html import strip_tags
import urllib
import json
import os

from .cart_views import *

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
env = settings.EXEC_ENV

def index(request):
	'''
	session_id = request.session.session_key
	dt = datetime.datetime.today()
	if session_id:
		ip_addr = get_ip_addr(request)
		ip_rec = User_ip_address.objects.filter(ip_address = ip_addr).first()
		if request.user.is_authenticated:
			usr = User.objects.get(username = request.user)
			usr_logged = True
		else:
			usr = None
			usr_logged = False
		if ip_rec:
			v_cnt = ip_rec.num_of_visits + 1
			i = User_ip_address.objects.filter(ip_address = ip_addr).update(
					latest_site_visit_datetime = dt, num_of_visits = v_cnt)
			s_id = ip_rec.session_id
			if s_id != session_id:
				## New session from the same ip...
				None
			else:
				## Same session from the same ip...
				None
		else:
			
			ip_rec = User_ip_address (
				session_id = session_id,
				userlogged_in =  usr_logged,
				user = usr,
				site_visit_datetime = dt,
				latest_site_visit_datetime = dt,
				num_of_visits = 1,
				ip_address = ip_addr
			)
			ip_rec.save()
	'''	
	return render(request, "artevenue/estore_base.html",{'env': env})


def offers(request) :
	return render(request, "artevenue/offers.html")


def contact_us(request):
	if request.method == 'POST':
		form = contactUsForm(request.POST)
		if form.is_valid():
			contact = form.save()
			return redirect('contact_msg')  
	else:
		form = contactUsForm()
		
	return render(request, "artevenue/contact_us.html", {'ecom_site':ecom, 'form':form})

def contact_msg(request):	
		return render(request, "artevenue/contactUs_confirm.html", {})

	
def about_us(request):

	return render(request, "artevenue/about_us.html", {})
	
def terms_conditions(request):

	return render(request, "artevenue/terms_of_use_apr2020.html", {})
	
def privacy_policy(request):

	return render(request, "artevenue/privacy_policy.html", {})
	
	
def faq(request):

	return render(request, "artevenue/faq.html")

def newsletter_subscription_confirmation(request):
	email = request.GET.get('email','')
	today = datetime.date.today()

	msg = 'SUCCESS'
	if email:
		try:
			e = Newsletter_subscription.objects.get(email = email, subscription_active = True)
		except Newsletter_subscription.DoesNotExist:
			ns = Newsletter_subscription(
				email = email,
				subscription_active = True,
				subscription_start_date = today,
				subscription_end_date = None
			)
			ns.save()
			msg = 'SUCCESS'
			return render(request, "artevenue/newsletter_subscription_confirmation.html",
				{'msg':msg, 'email':email})
		if e:
			msg = 'EXISTS'

		return render(request, "artevenue/newsletter_subscription_confirmation.html",
			{'msg':msg, 'email':email})

	
def show_prod_details(request):

	return render(request, "show_prod_details.html")
	

def show_frame(request) :
	return render(request, "show_frame.html")
	
@csrf_exempt	
def sync_cart_session_user(request, sessionid):

	# Get current session id
	#sessionid = request.session.session_key
	
	if sessionid is None:
		return JsonResponse({"status":"NOCART"})
	
	try:
		# Get usercart by session and user is None
		sessioncart = Cart.objects.get(session_id = sessionid, user = None, cart_status = "AC")
	except Cart.DoesNotExist:
		return JsonResponse({"status":"NOCART"})
	
	if sessioncart:
		if request.user.is_authenticated:
			try:
			
				# Check if the user already has a cart open
				user = User.objects.get(username = request.user)

				cart = Cart.objects.filter(user = user, cart_status = "AC")
				# User already has a cart open
				if cart:
					# Abondon the existing session cart
					cnt = cart.update(cart_status = 'AB', updated_date = datetime.datetime.now())
					'''
					updcart = Cart(
						cart_id = sessioncart.cart_id,
						store = sessioncart.store,
						session_id = sessioncart.session_id,
						user = user,
						voucher = sessioncart,
						voucher_disc_amount = sessioncart.voucher_disc_amount,
						quantity = sessioncart.quantity,
						cart_sub_total = sessioncart.cart_sub_total,
						cart_disc_amt  = sessioncart.cart_disc_amt,
						cart_tax  = sessioncart.cart_tax,
						cart_total = sessioncart.cart_total,
						cart_status = 'AB',
						created_date = sessioncart.created_date
					)						
					updcart.save()
					'''
					##return JsonResponse({"status":"CARTOPEN"})
			
				# Update the session Cart with current user id
				cnt_s = Cart.objects.filter(cart_id = sessioncart.cart_id).update(
						user = user, updated_date = datetime.datetime.now())
				'''
				updcart = Cart(
						cart_id = sessioncart.cart_id,
						store = sessioncart.store,
						session_id = sessioncart.session_id,
						user = user,
						voucher = sessioncart.voucher,
						voucher_disc_amount = sessioncart.voucher_disc_amount,
						quantity = sessioncart.quantity,
						cart_sub_total = sessioncart.cart_sub_total,
						cart_disc_amt  = sessioncart.cart_disc_amt,
						cart_tax  = sessioncart.cart_tax,
						cart_total = sessioncart.cart_total,
						cart_status = sessioncart.cart_status,
						created_date = sessioncart.created_date
				)						
				
				updcart.save()
				'''
				## Check is any order exists based on this cart, update it with the user
				order = Order.objects.filter(cart_id = sessioncart.cart_id).update(
					user = user, updated_date = datetime.datetime.now())
				
			finally:
				return JsonResponse({"status":"NOUSER"})
				
			return JsonResponse({"status":"SYNCHED"})
			
		else:
			return JsonResponse({"status":"NOUSER"})
	
	return JsonResponse({"status":"NOCART"})
	

@csrf_exempt					
def get_addr_pin_city_state(request):

	ipin_code = request.POST.get('pin_code', None)
	
	pin_code = {}
	city = {}
	cstate = {}
	country = {}

	if ipin_code :
		pin_codeObj = Pin_code.objects.filter(pin_code = ipin_code)
		pin_code = pin_codeObj.values("pin_code").distinct()
		city = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("city").distinct()
		cstate = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("state").distinct()
		country = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("country__country_name").distinct()
	else :
		pin_code = Pin_city_state_country.objects.values("pin_code").distinct()
		city = Pin_city_state_country.objects.values("city").distinct()
		cstate = Pin_city_state_country.objects.values("state").distinct()
		country = Pin_city_state_country.objects.values("country__country_name").distinct()

		
	return( JsonResponse({'pin_code':list(pin_code), 'city':list(city), 'cstate':list(cstate),
			'country':list(country)}, safe=False) )		


@csrf_exempt
def validate_address(request):
	ipin_code = request.POST.get('pin_code', None)
	icity = request.POST.get('city', None)
	icstate = request.POST.get('cstate', None)
	icountry = request.POST.get('country', None)

	msg = []
	err_flag = False

	if ipin_code is None or ipin_code == '':
		msg.append("Pin code cannot be empty")
		err_flag = True
	if icity is None or icity == '':
		msg.append("City cannot be empty")
		err_flag = True
	if icstate is None or icstate == '':
		msg.append("State cannot be empty")
		err_flag = True
	if icountry is None or icountry == '':
		msg.append("Country cannot be empty")
		err_flag = True
	
	q = Pin_city_state_country.objects.all()
	
	if ipin_code:
		q = q.filter(pin_code_id = ipin_code)
	if icity:
		q = q.filter(city_id = icity)
	if icstate:
		q = q.filter(state_id = icstate)
	if icity:
		cnt = Country.objects.filter(country_name = icountry).first()
		if not cnt :
			cnt = Country.objects.filter(country_code = icountry).first()
		q = q.filter(country = cnt)
	
	if q is None or q.count() == 0:
		msg.append("Entered Pin code, City, State is invalid. Please correct and then proceed.")
		err_flag = True

	if not err_flag:
		msg.append("SUCCESS")
	
	return JsonResponse({'msg':msg})

@login_required
def refer_us(request):
	today = datetime.date.today()
	msg = ''
	if request.method == 'POST':
		form = referralForm(request.POST, user=request.user)

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
		if (not result['success']) or (not result['action'] == 'referus'):
			msg = 'Invalid reCAPTCHA. Please try again.'
			return render(request, "artevenue/refer_us.html", {'form':form,
				'msg':msg})
		else :
			if form.is_valid():		
				refer = form.save(commit=False)			
				refer.referred_by = request.user
				refer.referred_date = today
				refer.save()
				return redirect('refer_confirm', ref_id=refer.id)  
	else:
		form = referralForm(user=request.user)
		
	return render(request, "artevenue/refer_us.html", {'form':form, 'msg':msg})

@login_required	
def refer_confirm(request, ref_id):
	
	try:
		referral = Referral.objects.get(id = ref_id)
		name = referral.name
	except Referral.DoesNotExist:
		name = "XXX"
		referral = None
	
	# Send mail
	subject = 'Your friend has a referred us, Artevenue.com. Log on and get rewarded!'
	html_message = render_to_string('artevenue/referral_email.html', 
			{'referral': referral})
	plain_message = strip_tags(html_message)
	from_email = 'support@artevenue.com'
	to = referral.email_id

	#cnt = send_mail(subject, plain_message, from_email, [to], html_message=html_message)

	msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
	msg.attach_alternative(html_message, "text/html")
	
	
	#msg = EmailMessage(subject, html_message, from_email, [to])
	#msg.content_subtype = "html"  # Main content is now text/html

	msg.send()	
	
	return render(request, "artevenue/refer_confirm.html", {'name':name})
	

@login_required
def egift_card(request):
	msg = ''
	today = datetime.date.today()
	if request.method == 'POST':
		gift_rec_id = request.GET.get('gift_rec_id','')
		 
		if gift_rec_id:
			gift = Egift.objects.get(gift_rec_id=gift_rec_id)
			form = egiftForm(request.POST  or None, instance=gift)
		else:
			form = egiftForm(request.POST, giver=request.user)
			

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
		if (not result['success']) or (not result['action'] == 'egift'):
			msg = 'Invalid reCAPTCHA. Please try again.'
			return render(request, "artevenue/egift_card.html", {'form':form,
				'msg':msg})
		else :
			if form.is_valid():		
				gift = form.save(commit=False)			
				gift.giver = request.user
				gift.gift_date = today
				gift.save()
				return redirect('egift_card_review', gift_rec_id=gift.gift_rec_id)  
	else:
		gift_rec_id = request.GET.get('gift_rec_id','')
		if gift_rec_id != '':
			gift = Egift.objects.get(gift_rec_id=gift_rec_id)	
			form = egiftForm(instance=gift)		
		else:
			form = egiftForm(giver=request.user, initial=({'gift_date':  today}) )
	
	# Card Designs
	designs = Egift_card_design.objects.all()
	
	return render(request, "artevenue/egift_card.html", {'form':form, 'msg':msg,
			'designs':designs})

@login_required
def egift_card_review(request, gift_rec_id):
	msg = ''
	gift = Egift.objects.get(gift_rec_id=gift_rec_id)
	form = egiftForm(instance = gift)

	# Card Designs
	designs = Egift_card_design.objects.all()
	
	return render(request, "artevenue/egift_card_review.html", {'form':form, 'msg':msg,
			'designs':designs, 'gift':gift})
	
def send_egift_mail(request, gift_rec_id):

	egift = Egift.objects.get(gift_rec_id = gift_rec_id)
	egift_card_design = Egift_card_design.objects.get(design_id = egift.egift_card_design_id)
	voucher = Voucher.objects.get(voucher_id = egift.voucher_id)
	voucher_user = Voucher_user.objects.filter(voucher = voucher, 
		used_date__isnull = True).first()

	#img_path = os.path.join(settings.EGIFT_DESIGNS, egift.egift_card_design.url)
	img_path = settings.EGIFT_DESIGNS + egift.egift_card_design.url

	card_img=Image.open(img_path)
	img_save_location = settings.STATIC_ROOT + '/egift_cards/' + str(egift.gift_rec_id) + '.jpg'
	img_url = 'http://artevenue.com/static/egift_cards/' + str(egift.gift_rec_id) + '.jpg'
	print(img_save_location)
	# use a truetype font
	try:
		font = ImageFont.truetype("arial.ttf", 18)
	except IOError as i:
		print(i)
	
	card_img = card_img.resize( (410, 256) )

	voucher_loc =  (20,20)
	amount_loc = (20,40)
	if egift_card_design.text_location == 'bottom-right':
		voucher_loc = (20,20)
		amount_loc = (314, 226)
	elif egift_card_design.text_location == 'top-left':
		voucher_loc = (20,20)
		amount_loc = (20, 40)
	color = egift_card_design.text_color

	# Print voucher code
	ImageDraw.Draw(
		card_img  # Image
	).text(
		voucher_loc,  # Coordinates
		'Coupan Code: ' + voucher.voucher_code,  # Text
		fill=color,  # Color
		font=font
	)

	# Print gift amount
	ImageDraw.Draw(
		card_img  # Image
	).text(
		amount_loc,  # Coordinates
		'Rs: ' + str(int(egift.gift_amount)),  # Text
		fill=color,  # Color
		font=font
	)
	card_img.save(img_save_location)

	# Send email to receiver
	subject = "A Gift for you from: " + egift.giver.first_name + " " + egift.giver.last_name + " (" + egift.giver.email + ")"
	html_message = render_to_string('artevenue/voucher_email.html', 
			{'voucher': voucher, 'voucher_user':voucher_user, 'egift':egift, 
			'img_url':img_url})
	plain_message = strip_tags(html_message)
	from_email = 'support@artevenue.com'
	to = egift.receiver_email
	emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
	emsg.attach_alternative(html_message, "text/html")
	emsg.send()
	print("Email sent to: " + to)
	
	return render(request, "artevenue/voucher_email_display.html", {'egift':egift, 
			'voucher_user':voucher_user, 'voucher':voucher, 'img_location':img_url})	

def send_order_emails():

	cus_paymnt = Payment_details.objects.filter(cust_email_sent = False)
	##### SEND EMAIL TO CUSTOMER
	for p in cus_paymnt:
		order = Order.objects.get(order_id = p.order_id)
		subject = "Arte'Venue Order placed successfully. Order No: " + order.order_number
		html_message = render_to_string('artevenue/order_print.html', 
				{'orders': order, 'email_id':p.email_id})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
		to = p.email_id
		msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
		msg.attach_alternative(html_message, "text/html")
		msg.send()	
	
	if cus_paymnt:
		cus_paymnt.update(cust_email_sent = True)

	fac_paymnt = Payment_details.objects.filter(factory_email_sent = False)
	##### SEND EMAIL TO CUSTOMER
	for p in fac_paymnt:
		order = Order.objects.get(order_id = p.order_id)
		subject = "Order No: " + order.order_number
		html_message = render_to_string('artevenue/factory_order_email.html', 
				{'referral': referral, 'host':request.get_host()})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
		to = "factory@artevenue.com"
		msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
		msg.attach_alternative(html_message, "text/html")
		msg.send()	

	if fac_paymnt:
		fac_paymnt.update(cust_email_sent = True)

		
	return
		

			
def countlines(start, extn, lines=0, header=True, begin_start=None):
	if header:
		print('{:>10} |{:>10} | {:<20}'.format('ADDED', 'TOTAL', 'FILE'))
		print('{:->11}|{:->11}|{:->20}'.format('', '', ''))

	for thing in os.listdir(start):
		thing = os.path.join(start, thing)
		if os.path.isfile(thing):
			if thing.endswith(extn):
				with open(thing, 'r') as f:
					newlines = f.readlines()
					newlines = len(newlines)
					lines += newlines

					if begin_start is not None:
						reldir_of_thing = '.' + thing.replace(begin_start, '')
					else:
						reldir_of_thing = '.' + thing.replace(start, '')

					print('{:>10} |{:>10} | {:<20}'.format(
							newlines, lines, reldir_of_thing))


	for thing in os.listdir(start):
		thing = os.path.join(start, thing)
		if os.path.isdir(thing):
			lines = countlines(thing, lines, header=False, begin_start=start)

	return lines
	
def how_to_customize(request):
	return render(request, "artevenue/how_to_customize.html") 
	
def how_to_hang(request):
	return render(request, "artevenue/how_to_hang.html") 	
	
def how_to_size(request):
	return render(request, "artevenue/how_to_size.html") 


def update_category_disp_priority():
	from artevenue.models import Stock_image, Curated_category

	priority = Curated_category.objects.all()
	print("Count: " + str(priority.count()))
	for p in priority:
		print("Processing..." + p.name )
		if p.banner_image_codes:
			ids = p.banner_image_codes.replace(' ','')
			ids = ids.split(",")
			cnt = 5
			for i in ids:
				if i is None or i == '':
					continue
				print("Updating..." + " Category: " + p.name + ", Id: " + str(i) )
				cnt = cnt + 1
				pr = (-1) * cnt
				prod = Stock_image.objects.filter(product_id = i).update(category_disp_priority = pr)
				if prod < 1:
					print("ID " + str(i) + " not found in category " + p.name)

				# check is this exists in respective curated category,
				# if not add it
				c = Curated_collection.objects.filter(product_id = i).first()
				if not c:
					print("ADDING==============>" + str(i))
					cc = Curated_collection(
						curated_category_id = p.category_id,
						product_id = i,
						product_type_id = 'STOCK-IMAGE'
					)

					cc.save()
	return


def update_curated_collections():
	from pathlib import Path
	import csv
	from artevenue.models import Curated_collection
	## 4692
	cfile = Path('C:/artevenue/DATA/CURATED_CATEGORIES_NEW_Jun2020/vastu_collections.csv')
	if not cfile.is_file():
		print("csv file not found.")
		return
	file = open('C:/artevenue/DATA/CURATED_CATEGORIES_NEW_Jun2020/vastu_collections.csv')
	cr = csv.reader(file, delimiter=',')
	
	cnt = 0
	for row in cr:
		if cnt == 0:	## Skipping first header row
			cnt = cnt + 1
			continue
		cnt = cnt + 1
		print("Processing...." + str(row[1]))
		prod_id = row[1]
		prod = None
		try:
			prod = Stock_image.objects.get(product_id = prod_id)
		except Stock_image.DoesNotExist:
			continue
		
		if prod:
			print("Updating...." + str(row[1]))
			n = Curated_collection(
				curated_category_id = row[0],
				product_id = row[1],
				product_type_id = 'STOCK-IMAGE'
			)
			
			n.save()
	print ("Count: " + str(cnt))
				


@staff_member_required
def order_management(request):
	return render(request, "artevenue/order_management.html")
	
				
@staff_member_required
def manage_order_details(request):
	today = datetime.datetime.today()
	msg = None

	if request.method == 'POST':		
	
		from artevenue.models import Order_sms_email, Voucher_used, Payment_details
		
		order_id = request.POST.get("order_id", "")
		process_order = request.POST.get("process_order", "")
		cancel_order = request.POST.get("cancel_order", "")

		order = Order.objects.filter(order_id = order_id).first()
		if order:
			cart = Cart.objects.filter(cart_id = order.cart_id).first()
		else:	
			cart = None
			
		if order_id:
			order = Order.objects.filter(order_id = order_id).first()
			if order:
				cart = Cart.objects.filter(cart_id = order.cart_id).first()
			else:	
				cart = None
		else:
			order = None
			cart = None
		
		if process_order == "PROCESS PAYMENT":
			o = Order.objects.filter(order_id = order_id).update(
				order_status = 'PC', order_date = today.date(),
				updated_date = today)
			c = Cart.objects.filter(cart_id = order.cart_id).update(cart_status = 'CO',
				updated_date = today)
			
			## Update referral records, if any
			if order.referral_disc_amount:
				if order.referral_disc_amount > 0:
					## Get referral record
					ref = Referral.objects.filter(id = order.referral_id)					
					## Check if user is a referrer or referee and update accordingly 
					for r in ref:
						if r.referred_by == order.user:
							ref_upd = Referral.objects.filter(id = order.referral_id).update(
								referred_by_claimed_date = today)
						elif r.email_id == order.user.email:
							ref_upd = Referral.objects.filter(id = order.referral_id).update(
								referee_claimed_date = today)			
			
			## Update the voucher used table, if a voucher was used
			if order.voucher_id and order.user:
				vu = Voucher_used( 
					voucher_id = order.voucher_id,
					user = order.user,
					created_date = today,
					updated_date = today
				)
				vu.save()
			

			# Update email, sms table
			o_email = Order_sms_email(
				order = order,
				customer_email_sent = False,
				factory_email_sent = False,
				customer_sms_sent = False,
				factory_sms_sent = False,
				created_date = today,	
				updated_date = today,
				customer_review_email_sent = False,
				customer_review_sms_sent = False
			)
			o_email.save()
			
			# Save the registration, subscription, payment, promotion code details 
			paymnt = Payment_details(
						first_name = order.order_billing.full_name,
						last_name = '',
						phone_number = order.order_billing.phone_number,
						email_id = order.order_billing.email_id,
						rec_id = order_id,
						payment_date = datetime.datetime.now(),
						amount = order.order_total,
						payment_txn_status = 'success',
						payment_txn_id = 'MANUAL',
						payment_txn_amount=None,
						payment_txn_posted_hash='',
						payment_txn_key='',
						payment_txn_productinfo= "Order Number " + order.order_number,
						payment_txn_email='',
						payment_txn_salt='',
						payment_firstname = '',
						payment_lastname = '',
						payment_email = '',
						payment_phone = '',
						payment_address1 = '',
						payment_address2 = '',
						payment_city = '',
						payment_state = '',
						payment_country = '',
						payment_zip_code = '',
						trn_type = 'ORD'
					)

			paymnt.save()
			msg = "PAYMENT FOR THIS ORDER IS PROCESSED"

		elif cancel_order == "CANCEL ORDER":
			o = Order.objects.filter(order_id = order_id).update(
				order_status = 'CN', 
				updated_date = today)
			c = Cart.objects.filter(cart_id = order.cart_id).update(cart_status = 'AB',
				updated_date = today)
			msg = "THIS ORDER IS CANCELLED"

		## Refetch order and cart to get updated status
		order = Order.objects.filter(order_id = order_id).first()
		if order:
			cart = Cart.objects.filter(cart_id = order.cart_id).first()
		else:	
			cart = None
			
			
	## GET request
	else:
		order_num = request.GET.get("order_num", "")
		cart_id = request.GET.get("cart_id", "")
		if order_num:
			order = Order.objects.filter(order_number = order_num).first()
			if order:
				cart = Cart.objects.filter(cart_id = order.cart_id).first()
			else:	
				cart = None
		elif cart_id:
			cart = Cart.objects.filter(cart_id = cart_id).first()
			order = Order.objects.filter(cart = cart).first()
		else:
			order = None
			cart = None

	
	cartitems = Cart_item_view.objects.select_related('product').filter(cart = cart,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	orderitems = Order_items_view.objects.select_related('product').filter(order = order,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
			
	return render(request, "artevenue/manage_order_details.html",
		{ 'msg': msg, 'env': env,
		 'order': order, 'cart': cart,
		 'orderitems': orderitems, 'cartitems': cartitems})	
	
@staff_member_required
def start_production(request):

	orders = Order.objects.filter(order_status = 'PC').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	msg = ""
	return render(request, "artevenue/orders_start_production.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'new_orders': orders, 'orderitems': orderitems, 'collage': collage})	

def set_in_production(request):
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'PR', updated_date =  today)
	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})


@staff_member_required
def make_ready_for_shipping(request):

	orders = Order.objects.filter(order_status = 'PR').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	msg = ""
	return render(request, "artevenue/make_ready_for_shipping.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'new_orders': orders, 'orderitems': orderitems, 'collage': collage})	
		 
def set_ready_for_shipping(request):
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	
	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'SH', updated_date =  today)
				
			if order.invoice_number == '':		# If ready for shipping, generate the invoice number
				from artevenue.views.invoice_views import get_next_invoice_number
				inv_num = get_next_invoice_number()
				ord = Order.objects.filter(order_id = order.order_id).update(
					invoice_number = inv_num, invoice_date = today)
			
			# Send email to customer - Ready for shipping
			#from artevenue.views import email_sms_views
			#email_sms_views.send_ord_update_sh(order_id)
			from artevenue.models import Order_status_communication
			os = Order_status_communication.objects.filter(order_id = order.order_id).first()
			if os:
				oe = Order_status_communication.objects.filter(order_id = order.order_id).update(
					ready_to_ship_sms_sent = False,
					ready_to_ship_email_sent = False
				)

			else:
				oe = Order_status_communication(
					order_id = order.order_id,
					tracking_info_sms_sent = False,
					tracking_info_email_sent = False,
					in_production_sms_sent = False,
					in_production_email_sent = False,
					ready_to_ship_sms_sent = False,
					ready_to_ship_email_sent = False
				)
				oe.save()
	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})

	
@staff_member_required
def order_shipping(request):
	from artevenue.models import Shipper, Shipping_method

	orders = Order.objects.filter(order_status = 'SH').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	shippers = Shipper.objects.all().order_by('name')
	shipping_methods = Shipping_method.objects.all().order_by('name')
	
	
	msg = ""
	return render(request, "artevenue/order_shipping.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'orders': orders, 'orderitems': orderitems, 'collage': collage,
		 'shippers': shippers, 'shipping_methods': shipping_methods})	

def make_in_transit(request):	
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	order_number = request.GET.get('order_number', '');
	shipper = request.GET.get('shipper', '');
	method = request.GET.get('method', '');
	track_no = request.GET.get('track_no', '');
	track_url = request.GET.get('track_url', '');
	ship_date = request.GET.get('ship_date', '');
	
	if shipper == '':
		sts = 'FAILURE'
		msg = 'Please select the shipper'
	
	if method == '':
		sts = 'FAILURE'
		msg = 'Please select the shipping method'

	if ship_date != '':
		shipDt = datetime.datetime.strptime(ship_date, "%Y-%m-%d")
	else:
		shipDt = None

	if sts == 'FAILURE':
		orders = Order.objects.filter(order_status = 'SH').order_by('order_date')
		orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
					product__product_type_id = F('product_type_id') ).order_by('product_id')
		
		c_ids = orderitems.values('product_id')
		collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
		
		shippers = Shipper.objects.all().order_by('name')
		shipping_methods = Shipping_method.objects.all().order_by('name')
		return render(request, "artevenue/order_shipping.html",
			{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(), 'order_number': order_number,
			 'orders': orders, 'orderitems': orderitems, 'collage': collage,
			 'shippers': shippers, 'shipping_methods': shipping_methods})	
		
	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'IN', shipper_id = shipper,
				shipping_method_id = method, tracking_number = track_no,
				shipment_date = shipDt, tracking_url = track_url,
				updated_date =  today)				

			## Email to customer, in case tracking number is updated			
			if track_no != '' :
				from artevenue.models import Order_status_communication
				os = Order_status_communication.objects.filter(order_id = order.order_id).first()
				if os:
					oe = Order_status_communication.objects.filter(order_id = order.order_id).update(
						tracking_info_sms_sent = False,
						tracking_info_email_sent = False
					)

				else:
					oe = Order_status_communication(
						order_id = order.order_id,
						tracking_info_sms_sent = False,
						tracking_info_email_sent = False,
						in_production_sms_sent = False,
						in_production_email_sent = False,
						ready_to_ship_sms_sent = False,
						ready_to_ship_email_sent = False
					)
					oe.save()

	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})


def order_dashboard(request):
	today = datetime.datetime.today()
	filter_applied = False
	
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	
	order_number = request.POST.get('order_number', '')
	order_status = request.POST.getlist('ORDER_STATUS')

	f_new = False
	f_in_production = False
	f_ready_for_shipping = False
	f_in_transit = False
	for o in order_status:
		if o == 'NEW':
			f_new = True
			filter_applied = True
		if o == 'IP':
			f_in_production = True
			filter_applied = True
		if o == 'RS':
			f_ready_for_shipping = True
			filter_applied = True
		if o == 'IN':
			f_in_transit = True
			filter_applied = True
			
			
	user_name = request.POST.get('user_name', '')
	user_email = request.POST.get('user_email', '')
	user_phone = request.POST.get('user_phone', '')
	printpdf = request.POST.get('printpdf', '')
	
	if printpdf == '':
		printpdf = request.POST.get('printpdf', 'NO')

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
		filter_applied = True
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
		filter_applied = True
		
	orders = Order.objects.exclude(order_status = 'CN').exclude(
				order_status = 'PP').exclude(order_status = 'CO').order_by('-order_date')

	if order_number:
		orders = orders.filter(order_number = order_number)
		filter_applied = True
	if user_email:
		orders = orders.filter(user__email__iexact = user_email)
		filter_applied = True
	if user_phone:
		orders = orders.filter(order_billing__phone_number = user_phone)
		filter_applied = True
	if user_name:
		orders = orders.filter(order_billing__full_name__icontains = user_name)
		filter_applied = True
	if startDt:
		orders = orders.filter(order_date__gte = startDt)
		filter_applied = True
	if endDt:
		orders = orders.filter(order_date__lte = endDt)
		filter_applied = True
		
	f = Q()
	if f_new:
		f = Q(order_status = 'PC')
		#orders = orders.filter(order_status = 'PC')
	if f_in_production:	
		f = (f | Q(order_status = 'PR'))
		#orders = orders.filter(order_status = 'PR')
	if f_ready_for_shipping:
		f = (f | Q(order_status = 'SH'))
		#order = orders.filter(order_status = 'SH')
	if f_in_transit:	
		f = (f | Q(order_status = 'IN'))
		#orders = orders.filter(order_status = 'IN')

	orders = orders.filter(f)
		
	new = orders.filter(order_status = 'PC').count()
	in_prod = orders.filter(order_status = 'PR').count()
	ready_for_shipping = orders.filter(order_status = 'SH').count()
	in_transit = orders.filter(order_status = 'IN').count()	

	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')

	return render(request, "artevenue/order_dashboard_details.html",
		{ 'ord_cnt': orders.count(), 'order': orders, 'order_number': order_number,
		 'orders': orders, 'orderitems': orderitems, 'collage': collage,
		 'startDt':startDt, 'endDt':endDt, 'user_email':user_email, 'user_phone':user_phone, 'user_name': user_name,
		 'new':new, 'in_prod':in_prod, 'ready_for_shipping':ready_for_shipping, 'in_transit':in_transit,
		'f_new': f_new, 'f_in_production' :f_in_production, 'f_ready_for_shipping' :f_ready_for_shipping,
		'f_in_transit' :f_in_transit, 'filter_applied' : filter_applied

		 })	

def print_pf_labels (request, order_id):
	from django.template.loader import render_to_string
	from weasyprint import HTML, CSS
	from django.core.files.storage import FileSystemStorage
	from artevenue.models import Publisher
	
	order = Order.objects.filter(order_id = order_id).first()
	orderitems = Order_items_view.objects.select_related('product').filter(order = order,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')

	publ = Publisher.objects.all()

	html_string = render_to_string('artevenue/printing_framing_label.html', {
		'order': order, 'orderitems': orderitems, 'collage': collage, 'MEDIA_URL':settings.MEDIA_URL,
		'ecom_site':ecom, 'publ': publ, 'env': env})

	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target= settings.TMP_FILES + order.order_number + '_printing_framing_label.pdf',
					presentational_hints=True);
	
	fs = FileSystemStorage(settings.TMP_FILES)
	with fs.open(order.order_number + '_printing_framing_label.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="' + order.order_number + '_printing_framing_label.pdf"'
		return response	

@staff_member_required
def order_delivery(request):
	from artevenue.models import Shipper, Shipping_method

	orders = Order.objects.filter(order_status = 'IN').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	shippers = Shipper.objects.all().order_by('name')
	shipping_methods = Shipping_method.objects.all().order_by('name')
	
	
	msg = ""
	return render(request, "artevenue/order_delivery.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'orders': orders, 'orderitems': orderitems, 'collage': collage,
		 'shippers': shippers, 'shipping_methods': shipping_methods})	

def set_order_delivery(request):
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	delivery_date = request.GET.get('delivery_date', '');
	
	if delivery_date != '':
		deliveryDt = datetime.datetime.strptime(delivery_date, "%Y-%m-%d")
	else:
		deliveryDt = None


	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'CO', delivery_date = deliveryDt, updated_date =  today)
	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})
	
	
@staff_member_required
def order_modification( request, order_id ):
	today = datetime.datetime.today()
	msg = None

	if order_id:
		order = Order.objects.filter(order_id = order_id).first()
		if order:
			cart = Cart.objects.filter(cart_id = order.cart_id).first()
		else:	
			cart = None
	else:
		order = None
		cart = None

	if order:
		order_items = Order_items_view.objects.select_related('product').filter(order = order,
					product__product_type_id = F('product_type_id') ).order_by('product_id')
		c_ids = order_items.values('product_id')
		collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	else: 
		order_items = None
		collage = None

	return render(request, "artevenue/order_modification.html",
			{ 'msg': msg, 'env': env,
			 'order': order, 'order_items': order_items, 'collage': collage,
			 })	
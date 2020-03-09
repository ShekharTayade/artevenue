from django.shortcuts import render, get_object_or_404
from datetime import datetime
import datetime
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

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

from .cart_views import *

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )

def index(request):
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
		
	return render(request, "artevenue/estore_base.html",{})


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

	return render(request, "artevenue/tnc_26jun2019.html", {})
	
def privacy_policy(request):

	return render(request, "artevenue/privacy_policy.html", {})
	
	
def faq(request):

	return render(request, "artevenue/faq.html")

def newsletter_subscription_confirmation(request):
	email = request.GET.get('email','')

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
		


			
	
from django.shortcuts import render, get_object_or_404
from datetime import datetime
import datetime
from django.db import IntegrityError, DatabaseError, Error

from artevenue.models import Ecom_site, Cart
from artevenue.forms import contactUsForm

from artevenue.models import Pin_code, City, State, Country, Pin_city_state_country

from django.http import HttpResponse
from django.conf import settings

from .cart_views import *

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )

def index(request):


	return render(request, "artevenue/estore_base.html",{})


def contact_us(request):

	if request.method == 'POST':
		form = contactUsForm(request.POST)
		if form.is_valid():
			contact = form.save()
			return redirect('index')  
	else:
		form = contactUsForm()
		
	return render(request, "artevenue/contact_us.html", {'ecom_site':ecom, 'form':form})

def contact_msg(request):	
		return render(request, "artevenue/contactUs_confirm.html", {})

	
def about_us(request):

	return render(request, "artevenue/about_us.html")
	
def terms_conditions(request):

	return render(request, "terms_conditions.html")

	
def faq(request):

	return render(request, "faq.html")
	
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
				userid = User.objects.get(username = request.user)

				cart = Cart.objects.filter(user = userid, cart_status = "AC")
				# User already has a cart open, then return
				if cart:
					# Abondon the existing session cart & return back
					updcart = Cart(
						cart_id = sessioncart.cart_id,
						product_type_id = sessioncart.product_type_id,
						store = sessioncart.store,
						session_id = sessioncart.session_id,
						user_id = userid,
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
					return JsonResponse({"status":"CARTOPEN"})
			
				# Update the session Cart with current user id
				updcart = Cart(
						cart_id = sessioncart.cart_id,
						product_type_id = sessioncart.product_type_id,
						store = sessioncart.store,
						session_id = sessioncart.session_id,
						user_id = userid,
						voucher = sessioncart,
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
		q = q.filter(country = cnt)
	
	if q is None or q.count() == 0:
		msg.append("Entered Pin code, City, State is invalid. Please correct and then proceed.")
		err_flag = True

	if not err_flag:
		msg.append("SUCCESS")
	
	return JsonResponse({'msg':msg})
		
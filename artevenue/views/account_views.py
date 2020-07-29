from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth import login as auth_login
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.db.models import Count, Q, Max, Sum

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.urls import resolve
from django.contrib import messages
import datetime
from dateutil.relativedelta import relativedelta 
import calendar

from artevenue.forms import registerForm, businessprofile_Form, businessuserForm
from artevenue.forms import businessprof_Form, userProfileForm
from artevenue.forms import userForm, shipping_addressForm, billing_addressForm
from artevenue.forms import OrderStatusUpdate
from artevenue.models import Pin_code, Business_profile, User_shipping_address, Promotion_voucher
from artevenue.models import Promotion_voucher, Voucher_user, UserProfile, Business_referral_fee
from artevenue.models import User_billing_address, Order, Order_items_view, Cart_item_view
from artevenue.models import Channel_partner

from artevenue.models import Egift, Egift_redemption, User_sms_email, Business_referral_fee
from artevenue.models import Country, State, City, Pin_code, Order_deferred_payment

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML, CSS

from .views import *
from artevenue.views import email_sms_views

ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
today = datetime.datetime.today()

def artevenuelogin(request):
	if request.method == 'POST':
    
		# Get current session details
		sessionid = request.session.session_key
	
		
		username = request.POST['username'] 
		password = request.POST['password']
		email = request.POST['email']
		next = request.POST['curr_pg']
		
		user = authenticate(request, email=email, username=username, password=password)
	   
		if user is not None :
            
			login(request, user)
			
			if not request.POST.get('remember', None):
				request.session.set_expiry(0)   
	
			# Let's sync the cart for the session and logged in user
			sync_cart_session_user(request, sessionid)
	
			return redirect(next)
        
		else :
			messages.add_message(request, messages.ERROR, 'Your credentials did not match. Please try again.')		
			return redirect(next)
			#return render(request, 'artevenue/estore_base.html', {
			#	'username' : request.user.username, 'auth_user' : 'FALSE'})
	else:
		# This is required as front checks for message object and displays
		# login dialog box only when the message objects is present
		if not request.user.is_authenticated:
			messages.add_message(request, messages.INFO, 'Nothing')		
		
		return render(request, 'artevenue/estore_base.html')

	
def register(request, email=None, signup_popup = 0):
	today = datetime.datetime.today()

	## Get any sign up promotion
	try:
		promo_voucher = Promotion_voucher.objects.get(promotion__name = 'SIGN-UP',
			promotion__effective_from__lte = today.date(),
			promotion__effective_to__gte = today.date())
	except Promotion_voucher.DoesNotExist:
			promo_voucher = None
	if promo_voucher:
		promotion_id = promo_voucher.promotion.promotion_id
	else:
		promotion_id = None
	msg =''
	business_code = ''
	if request.method == 'POST':	
		next = request.POST['curr_pg']
		form = registerForm(request.POST)
		business_code = request.POST.get('business_code', None)

		'''
		# get the token submitted in the form
		recaptcha_response = request.POST.get('signup-recaptcha')
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
		if (not result['success']) or (not result['action'] == 'signup'):
			msg = 'Invalid reCAPTCHA. Please try again.'
			return render(request, "artevenue/register.html", {'form':form,
					'msg':msg, 'promo_voucher':promo_voucher} )
		else :	
		'''
		bus_profile = None
		if form.is_valid():
			## validate the business code
			if business_code:
				try:
					bus_profile = Business_profile.objects.get(business_code = business_code)
				except Business_profile.DoesNotExist:
					msg = "The business referral code you entered does not exist. Please check the code and try again."
					bus_profile = None
					return render(request, "artevenue/register.html", {'form':form, 
							'promo_voucher':promo_voucher, 'msg':msg, 'business_code':business_code} )

			user = form.save()
			auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

			# Update email, sms table
			tday = datetime.datetime.today()
			u_email = User_sms_email(
				user = user,
				welcome_email_sent = False,
				welcome_sms_sent = False,
				created_date = tday,	
				updated_date = tday
			)
			u_email.save()
			
			## Create voucher for current user, in case of any running promotion 
			if promotion_id:
				ret = create_user_voucher_for_promo(request, promotion_id)
			
			if bus_profile:
				u_profile = UserProfile(
					user = user,
					phone_number = '',
					date_of_birth = None,
					gender = '',
					business_profile = bus_profile )
					
				u_profile.save()
			# After successful sign up redirect to cuurent page
			if signup_popup == 1:
				next = request.POST['curr_pg']
				return redirect(next)
			else:
				return redirect('index')
	else:
		email = request.GET.get('email', '')
		if email:
			form = registerForm({'email':email})
		else:
			form = registerForm()
		
	return render(request, "artevenue/register.html", {'form':form, 
			'promo_voucher':promo_voucher, 'msg':msg, 'business_code':business_code} )
	
	
def business_registration(request):
	today = datetime.datetime.today()
    
	if request.method == 'POST':

		form = businessuserForm(request.POST)
		businessprofile_form = businessprofile_Form(request.POST)
		channel_partner = request.POST.get('channel_partner', None)

		if form.is_valid():
			if businessprofile_form.is_valid():
				if channel_partner:
					try:
						chn = Channel_partner.objects.get(partner_code = channel_partner)
					except Channel_partner.DoesNotExist:
						msg = "The channel partner code you entered does not exist. Please check the code and try again."
						bus_profile = None
						return render(request, 'artevenue/business_registration.html', {'form': form, 
							'businessprofile_form': businessprofile_form, 'msg':msg})

				user = form.save()
				auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				# Update email, sms table
				u_email = User_sms_email(
					user = user,
					welcome_email_sent = False,
					welcome_sms_sent = False,
					created_date = today,	
					updated_date = today
				)
				u_email.save()
				
				userprofile = businessprofile_form.save(commit=False)
				userprofile.user = user
				userprofile.save()
			
				# After successful sign up redirect to payment page
				return render(request, 'artevenue/business_registration_confirm.html', {'form': form, 
					'businessprofile_form': businessprofile_form, 'channel_partner':channel_partner})
	else:
		form = businessuserForm()
		businessprofile_form = businessprofile_Form()		
	return render(request, 'artevenue/business_registration.html', {'form': form, 'businessprofile_form': businessprofile_form})

	
@login_required
def my_account(request):
	msg = ""
	businessprofile_form = {}
	profile={}
	shipping_form ={}
	billing_form ={}
	user_ProfileForm = {}
	business_code = ''
	curruser = get_object_or_404(User, username = request.user)

	
	try:
		chn = Channel_partner.objects.get(user = curruser)
		channel_partner = chn.partner_code
	except Channel_partner.DoesNotExist:
		channel_partner = ''
	
	try:
		curruser_profile = UserProfile.objects.get(user = curruser)
		if curruser_profile:
			if curruser_profile.business_profile :
				business_code = curruser_profile.business_profile.business_code
			else:
				business_code = None
		else:
			business_code = None
		
	except UserProfile.DoesNotExist:
		curruser_profile = None

	if request.method == 'POST':
	
		import pdb
		pdb.set_trace()
	
		if request.POST.get('u_form', 'NONE') != 'NONE':
			user_form = userForm( request.POST, instance=request.user )
			if user_form.is_valid():
				u = user_form.save()
				msg = "Changes to your Arte'Venue account saved."

		if request.POST.get('b_form', 'NONE') != 'NONE':
			businessprofile_form = businessprof_Form( request.POST )
			if businessprofile_form.is_valid():
				profile = Business_profile.objects.get( user = curruser )
				b = businessprofile_form.save(commit=False)
				b.user = curruser
				b.created_date = profile.created_date
				b.id = profile.id
				b.profile_group = profile.profile_group
				b.approval_date = profile.approval_date
				b.save()
				msg = "Changes to your business account profile saved."

		if request.POST.get('prof_form', 'NONE') != 'NONE':			
			user_ProfileForm = userProfileForm( request.POST, prefix = 'prof' )
			if user_ProfileForm.is_valid():
				u = user_ProfileForm.save(commit=False)
				id = user_ProfileForm['id'].data
				if id:
					u.id = id					
				bus_code = user_ProfileForm['business_referral_code'].data
				if bus_code:
					try:
						profile = Business_profile.objects.get( business_code = bus_code )
						business_code = profile.business_code
						u.business_profile = profile
						msg = "Changes to your profile saved."
						u.user = curruser
						u.save()
					except Business_profile.DoesNotExist:
						msg = 'The entered business referral code is not valid. Please check and try again.'
				else:
					msg = "Changes to your profile saved."
					u.user = curruser
					u.save()
		
		if request.POST.get('ship_form', 'NONE') != 'NONE':
			shipping_form = shipping_addressForm( request.POST, prefix = 'ship' )
			if shipping_form.is_valid():
				ship_addr = shipping_form.save()
				msg = "Changes to your shipping address saved."
				
		if request.POST.get('bill_form', 'NONE') != 'NONE':
			billing_form = billing_addressForm( request.POST, prefix = 'bill' )
			if billing_form.is_valid():
				bill_addr = billing_form.save()
				msg = "Changes to your billing address saved."
			
				
	# Get user id
	user_form = userForm( instance = curruser )

	if not businessprofile_form:
		try:
			profile = Business_profile.objects.get( user = curruser )
			businessprofile_form = businessprof_Form( instance = profile )
		except Business_profile.DoesNotExist:
			profile = {}
			businessprofile_form = {}

	if not user_ProfileForm:
		if curruser_profile:
			if businessprofile_form:
				user_ProfileForm = userProfileForm( instance = curruser_profile, prefix = 'prof',
				initial={'user_id':curruser.id, 'business_profile': curruser_profile.business_profile_id,
					'business_referral_code':profile.business_code})
			else:
				if curruser_profile:
					if curruser_profile.business_profile:
						b_code = curruser_profile.business_profile.business_code
					else:
						b_code = None
				else: 	
						b_code = None
				user_ProfileForm = userProfileForm( instance = curruser_profile, prefix = 'prof',
				initial={'user_id':curruser.id, 'business_profile': curruser_profile.business_profile_id,
					'business_referral_code':b_code})
		else:
			if businessprofile_form:
				user_ProfileForm = userProfileForm(prefix = 'prof', initial={'user_id':curruser.id,
					'business_referral_code':profile.business_code})
			else:
				user_ProfileForm = userProfileForm(prefix = 'prof', initial={'user_id':curruser.id})
		
		
	if not shipping_form:
		shipping_addr = User_shipping_address.objects.filter( user = curruser ).first()
		shipping_form = shipping_addressForm( instance = shipping_addr, 
			prefix = 'ship', initial={'user':curruser.id})
	if not billing_form:
		billing_addr = User_billing_address.objects.filter( user = curruser ).first()
		billing_form = billing_addressForm( instance = billing_addr, 
			prefix = 'bill', initial={'user':curruser.id})

	country_list = Country.objects.all()
	country_arr = []
	for c in country_list:
		country_arr.append(c.country_name)
		
	state_list = State.objects.all()
	state_arr = []
	for s in state_list:
		state_arr.append(s.state_name)		
	
	city_list = City.objects.all()
	city_arr = []
	for ct in city_list:
		city_arr.append(ct.city)
	
	pin_code_list = Pin_code.objects.all()
	pin_code_arr = []
	for p in pin_code_list:
		pin_code_arr.append(p.pin_code)
		
	## Check for any egifts as giver, receiver
	
	## Giver
	egift_giver = Egift.objects.filter(giver = curruser)
	egift_redemption = {}
	if egift_giver:
		eg_ids = Egift.objects.filter(giver = curruser).values('gift_rec_id')
		egift_redemption = Egift_redemption.objects.filter(
			egift_id__in = eg_ids).order_by('egift')
	
	## Receiver
	egift_receiver = Egift.objects.filter(receiver_email = curruser.email).order_by('gift_rec_id')
	redemptions = {}
	if egift_receiver:
		eg_ids = Egift.objects.filter(receiver_email = curruser.email).values('gift_rec_id')
		egift_redemption = Egift_redemption.objects.filter(
			egift_id__in = eg_ids).order_by('egift').order_by('egift_id')
		
		redemptions = Egift_redemption.objects.filter(egift_id__in = eg_ids).values(
			'egift_id').annotate(total_claimed=Sum('redemption_amount'))
			
	
	return render(request, 'artevenue/my_account.html', {'msg':msg,
		'user_form':user_form, 'user_ProfileForm':user_ProfileForm,
		'businessprofile_form':businessprofile_form, 'business_code':business_code,
		'shipping_form':shipping_form, 'billing_form':billing_form,
		'egift_giver':egift_giver, 'egift_receiver':egift_receiver,
		'egift_redemption':egift_redemption, 'redemptions':redemptions,
		'country_arr':country_arr, 'state_arr':state_arr,
		'city_arr':city_arr, 'pin_code_arr':pin_code_arr,
		'channel_partner':channel_partner} )


@login_required
def my_orders(request):
	
	return render(request, 'artevenue/my_orders.html')		

@login_required
@csrf_exempt
def get_orders(request):


	#import logging
	#logger = logging.getLogger('weasyprint')
	#if settings.EXEC_ENV == 'DEV' or settings.EXEC_ENV == 'TESTING':
	#	logger.addHandler(logging.FileHandler('/weasyprint/log/weasyprint.log'))
	#	
	#if settings.EXEC_ENV == 'PROD':
	#	logger.addHandler(logging.FileHandler(settings.PROJECT_DIR + '/weasyprint/log/weasyprint.log'))

	
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	ordtype = request.POST.get('ordtype', 'U')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")

	if ordtype == 'U':
		user = User.objects.get(username = request.user)
		order_list = Order.objects.filter(user = request.user).order_by('order_number')
	else:
		order_list = Order.objects.all().order_by('-updated_date')
	
	order_items_list = {}
	if startDt:
		order_list = order_list.filter(order_date__gte = startDt)
	if endDt:
		order_list = order_list.filter(order_date__lte = endDt)
	'''
	order_items_list = Order_items_view.objects.filter(
		order__in = order_list, product__product_type_id = F('product_type_id')).select_related('product', 'promotion').values(
		'order_item_id', 'product_id', 'quantity', 'item_total', 'item_sub_total', 'item_tax', 'item_disc_amt',
		'moulding_id', 'item_unit_price', 'product__image_to_frame',
		'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
		'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height',
		'product__thumbnail_url', 'promotion__discount_value', 'product__publisher',
		'promotion__discount_type', 'mount__color', 'order_id',  'product_type',
		'product__image_to_frame_thumbnail'
		).order_by('order_id')
	'''
	order_items_list = Order_items_view.objects.filter(
		order__in = order_list, product__product_type_id = F('product_type_id')).select_related('product', 'promotion')

	count = order_list.count()

	
	paginator = Paginator(order_list, 5)
	orders = paginator.get_page(page)
	try:
		orders = paginator.page(page)
	except PageNotAnInteger:
		orders = paginator.page(1)
	except EmptyPage:
		orders = paginator.page(paginator.num_pages)

		
	if printpdf == "YES":
		#html_string = render_to_string('artevenue/orders_table.html', {'count':count, 
		html_string = render_to_string('artevenue/order_print.html', {'count':count, 
			'orders': order_list, 'order_items_list':order_items_list, 
			'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL,
			'MEDIA_ROOT':settings.MEDIA_ROOT})

		html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
		
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_ord_pdf.pdf',
			stylesheets=[
						CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
						],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_ord_pdf.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_ord_pdf.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/orders_table.html', {'count':count, 
			'orders': orders, 'order_items_list':order_items_list, 
			'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL})		

			
@staff_member_required
def store_orders(request):
	return render(request, 'artevenue/store_orders.html')	

## Used for unautheticated users, to locate their orders by order number or email id
def find_orders(request):
	return render(request, 'artevenue/find_orders.html')	
	

@csrf_exempt
def get_store_orders(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	order_number = request.POST.get("order_number", '')

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
		
	order_list = Order.objects.filter().select_related('order_billing', 
		'order_shipping').order_by('-updated_date')
		
	order_items_list = {}
	if startDt:
		order_list = order_list.filter(order_date__gte = startDt)
	if endDt:
		order_list = order_list.filter(order_date__lte = endDt)

	if order_number:
		order_list = order_list.filter(order_number = order_number)	
	
	if	not startDt and not endDt and not order_number:
		return render(request, 'artevenue/orders_table.html', {'count':0, 
			'orders': {}, 'order_items_list':{}, 
			'startDt':startDt, 'endDt':endDt})
	'''		
	order_items_list = Order_items_view.objects.select_related('product', 'promotion').filter(
		order__in = order_list, product__product_type_id = F('product_type_id')).values(
		'order_item_id', 'product_id', 'quantity', 'item_total', 'item_sub_total', 'item_tax', 'item_disc_amt',
		'moulding_id', 'item_unit_price', 'product__image_to_frame',
		'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
		'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height',
		'product__thumbnail_url', 'promotion__discount_value', 
		'promotion__discount_type', 'mount__color', 'order_id',  'product_type'
		).order_by('order_id')

	'''
	order_items_list = Order_items_view.objects.select_related('product', 'promotion').filter(
		order__in = order_list, product__product_type_id = F('product_type_id'))
	
	count = order_list.count()
	
	paginator = Paginator(order_list, 5)
	orders = paginator.get_page(page)
	try:
		orders = paginator.page(page)
	except PageNotAnInteger:
		orders = paginator.page(1)
	except EmptyPage:
		orders = paginator.page(paginator.num_pages)

		
	if printpdf == "YES":
		#html_string = render_to_string('artevenue/store_orders_table.html', {'count':count, 
		html_string = render_to_string('artevenue/order_print.html', {'count':count, 
			'orders': order_list, 'order_items_list':order_items_list, 
			'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL})

		html = HTML(string=html_string, base_url=request.build_absolute_uri())
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_ord_pdf.pdf',
			stylesheets=[CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') ]);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_ord_pdf.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_ord_pdf.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/orders_table.html', {'count':count, 
			'orders': orders, 'order_items_list':order_items_list, 
			'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL,
			'count': count})		

@staff_member_required
def orders_for_status_update(request):
	return render(request, 'artevenue/orders_for_status.html', {})

@csrf_exempt	
def get_orders_for_status_update(request):
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	order_number = request.POST.get("order_number", '')
	fetch_again = request.POST.get("fetch_again", None)
	
	order_list = Order.objects.exclude(
		Q(order_status = 'PP') | Q(order_status = 'CO')
		).select_related('order_billing', 
		'order_shipping').order_by('-order_date')
		
	order_items_list = {}
	if order_number:
		order_list = order_list.filter(order_number = order_number)	
	
	order_items_list = Order_items_view.objects.select_related('product', 'promotion').filter(
		order__in = order_list, product__product_type_id = F('product_type_id'))
	
	count = order_list.count()
	
	paginator = Paginator(order_list, 25)
	orders = paginator.get_page(page)
	try:
		orders = paginator.page(page)
	except PageNotAnInteger:
		orders = paginator.page(1)
	except EmptyPage:
		orders = paginator.page(paginator.num_pages)

	if fetch_again:		
		return render(request, 'artevenue/orders_for_status_update_table.html', {'count':count, 
			'orders': orders, 'order_items_list':order_items_list})		
	else:
		return render(request, 'artevenue/orders_for_status_update.html', {'count':count, 
			'orders': orders, 'order_items_list':order_items_list})		

	
@staff_member_required
@csrf_exempt
def update_order_status(request, order_id = None, order_status =  None):
	today = datetime.datetime.today()
	
	if order_id and order_status:
		order = Order.objects.filter(order_id = order_id).update(
			order_status = order_status, updated_date = today )
		msg = "Order Status Updated"
		return JsonResponse({'msg':'Order Status Updated.'}, safe=False)
	if request.method == 'POST':
		order_id = int(request.POST.get('order_id', '0'))
		order_status = request.POST.get('order_status', '')
		shipper = request.POST.get('shipper', '')
		shipping_method = request.POST.get('shipping_method', '')
		tracking_number = request.POST.get('tracking_number', '')
		shipment_date = request.POST.get('shipment_date', '')
		tracking_url = request.POST.get('tracking_url', '')

		if shipment_date != '':
			ship_date = datetime.datetime.strptime(shipment_date, "%Y-%m-%d")		
		else:
			ship_date = None

		order = Order.objects.get(order_id = order_id)
		## validate uniue tracking number
		if order.tracking_number != tracking_number:	# check only if it's not the same tracking number on this order
			if tracking_number != '':
				tr = Order.objects.filter(tracking_number = tracking_number).first()
				if tr :
					return JsonResponse({'status': 'FAILURE',
						'msg':'Order update not done. Tracking number ' + tracking_number + ' already exists for order number ' + str(tr.order_number)}, 
						safe=False)			

		if order_status == 'SH' and order.invoice_number == '':		# If ready for shipping, generate the invoice number
			from artevenue.views.invoice_views import get_next_invoice_number
			inv_num = get_next_invoice_number()
			ord = Order.objects.filter(order_id = order_id).update(
				order_status = order_status, updated_date = today,
				invoice_number = inv_num, invoice_date = today)
		else:	
			ord = Order.objects.filter(order_id = order_id).update(
				order_status = order_status, updated_date = today,
				shipper_id = shipper, shipping_method_id = shipping_method,
				tracking_number = tracking_number, shipment_date = ship_date,
				tracking_url = tracking_url)
							
		msg = "Order Status Updated"			

		if order_status == 'SH' :
			email_sms_views.send_ord_update_sh(order_id)
			
		## Email to customer, in case tracking number is updated
		if tracking_number != '' and tracking_number != order.tracking_number:
			email_sms_views.send_tracking_no_to_cust(order_id)
		
		return JsonResponse({'status': 'SUCCESS', 
			'msg':'Order Status Updated.'}, safe=False)
	else:
		order_id = int(request.GET.get('order_id', '0'))
		order = Order.objects.get(order_id = order_id)
		form = OrderStatusUpdate(instance = order)
		return  render(request, 'artevenue/order_status_update_modal.html', 
			{'form':form, 'order':order})
		


@login_required
def create_user_voucher_for_promo(request, promotion_id):
	today = datetime.datetime.today()

	msg = ''

	## Get current user
	user = User.objects.get(username = request.user)
	if not user:
		return ({'msg':'NO-USER'})		

	## Get the voucher record
	try:
		promo_voucher = Promotion_voucher.objects.get(promotion__promotion_id = promotion_id,
				promotion__effective_from__lte = today.date(),
				promotion__effective_to__gte = today.date())
	except Promotion_voucher.DoesNotExist:
			promo_voucher = None
	
	if not promo_voucher:
		return ({'msg':'NO-PROMO'})

	voucher_user = Voucher_user(
		voucher_id = promo_voucher.voucher.voucher_id,
		user = user,
		effective_from = today,
		effective_to = promo_voucher.promotion.effective_to,
		used_date = None,
		created_date = today,
		updated_date = today
		)
	voucher_user.save()
	msg = "SUCCESS"

	return ({'msg':msg})


@staff_member_required
def store_carts(request):
	return render(request, 'artevenue/store_carts.html')	

@staff_member_required		
@csrf_exempt
def get_carts(request, printpdf=''):
	today = datetime.datetime.today()
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	today = datetime.datetime.today()
	
	no_checkout_carts = request.POST.get('no_checkout_carts', '')
	all_carts = request.POST.get('all_carts', '')
	no_payment_carts = request.POST.get('no_payment_carts', '')
	payment_done_carts = request.POST.get('payment_done_carts', '')
	user_email =  request.POST.get('user_email', '')
	carts_opt =  request.POST.get('carts_opt', '')
	
	if printpdf == '':
		printpdf = request.POST.get('printpdf', 'NO')

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
		
	cart_list = Cart.objects.order_by('-updated_date').exclude(cart_status = 'AB')
	
	if startDt:
		cart_list = cart_list.filter(updated_date__date__gte = startDt)
	if endDt:
		cart_list = cart_list.filter(updated_date__date__lte = endDt)

	if user_email:
		cart_list = cart_list.filter(user__email = user_email)

	if	carts_opt == 'NO-CHK':
		## Remove the carts that already have an order created against
		for c in cart_list:
			ord = Order.objects.filter( cart_id = c.cart_id).first()
			if ord:
				cart_list = cart_list.exclude(cart_id = c.cart_id)
			
	if	carts_opt == 'CHK':
		## Remove the carts that have an order created against but no payment done
		for c in cart_list:
			ord = Order.objects.filter( cart_id = c.cart_id).first()
			if ord:
				if ord.order_status != 'PP':
					cart_list = cart_list.exclude(cart_id = c.cart_id)
			else:
				cart_list = cart_list.exclude(cart_id = c.cart_id)
	
	if	carts_opt == 'PAY-DONE':
		## Remove the carts that have an order created and payment is done
		for c in cart_list:
			ord = Order.objects.filter( cart_id = c.cart_id).first()
			if ord:
				if ord.order_status == 'PP':
					cart_list = cart_list.exclude(cart_id = c.cart_id)
			else:
				cart_list = cart_list.exclude(cart_id = c.cart_id)
	
	if	not startDt and not endDt:
		return render(request, 'artevenue/carts_table.html', {'count':0, 
			'startDt':startDt, 'endDt':endDt})
	cart_items_list = Cart_item_view.objects.select_related('product').filter(
		cart__in = cart_list, product__product_type_id = F('product_type_id'))
			
	count = cart_list.count()

	created_count = None
	updated_count =None
	carts_value  = None
	orders_count = None
	orders_value = None

	created_count = cart_list.filter(created_date__date = today.date() ).count()
	updated_count = cart_list.filter(updated_date__date = today.date() ).count()
	carts_value = cart_list.filter(updated_date__date = today.date() ).aggregate( c_total=Sum( 'cart_total') )

	cart_list_ids = cart_list.values('cart_id')
	orders = Order.objects.filter( cart__in = cart_list_ids)
	orders_value = orders.filter(order_date = today.date()).aggregate( o_total=Sum( 'order_total') )
	orders_count = orders.filter(order_date = today.date()).count()
	
	paginator = Paginator(cart_list, 10)
	carts = paginator.get_page(page)
	
	try:
		carts = paginator.page(page)
	except PageNotAnInteger:
		carts = paginator.page(1)
	except EmptyPage:
		carts = paginator.page(paginator.num_pages)
	
	if printpdf == "YES":
		html_string = render_to_string('artevenue/carts_print.html', {'count':count, 
			'carts': carts, 'cart_items':cart_items_list, 'orders':orders,
			'startDt':startDt, 'endDt':endDt, 'ecom_site':ecom,
			'created_count': created_count, 'updated_count' : updated_count, 
			'carts_value': carts_value, 'orders_count': orders_count, 
			'orders_value': orders_value})

		html = HTML(string=html_string, base_url=request.build_absolute_uri())
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_cart_pdf.pdf',
			stylesheets=[CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') ],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_cart_pdf.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_cart_pdf.pdf"'
			return response

		return response		
	else:
		
		return render(request, 'artevenue/carts_table.html', {'count':count, 
			'carts': carts, 'cart_items':cart_items_list,  'orders':orders, 
			'startDt':startDt, 'endDt':endDt, 'ecom_site':ecom,
			'created_count': created_count, 'updated_count' : updated_count, 
			'carts_value': carts_value, 'orders_count': orders_count, 
			'orders_value': orders_value})


def referral_fee_month_process(yrmonth=''):

	#########################################
	## Move all orders to referral fee table
	## For current  month
	#########################################
	today = datetime.datetime.today()
	
	if yrmonth == '':
		last_mth_yr = datetime.datetime.now() - relativedelta(months=1)
		mth = str(last_mth_yr.month)
		year = str(last_mth_yr.year)
		yrmonth = year + '-' + mth
	else:
		last_mth_yr = datetime.datetime.strptime(yrmonth + '-01', "%Y-%m-%d").date()	
	
	process_start_date = datetime.datetime.strptime(yrmonth + '-01', "%Y-%m-%d").date()	
	month_days = calendar.monthrange(last_mth_yr.year, last_mth_yr.month)[1]
	process_end_date = datetime.datetime.strptime(yrmonth + '-' + str(month_days), "%Y-%m-%d").date()

	business_profiles = Business_profile.objects.all().order_by('id')
	for b in business_profiles:
	
		if b.created_date.year > process_end_date.year:
			continue
		###########################################
		## Get total sale in last one user year  ##
		###########################################
		year_start_date = None
		## Get start date of last 1 user year
		if b.created_date.year == process_end_date.year:
			year_start_date = b.created_date
		else:
			day = str(b.created_date.day)
			mth = str(b.created_date.month)
			yr = str(process_end_date - relativedelta(years=1).year)
			year_start_date = datetime.datetime.strptime(yr + '-' + mth + '-' + day, "%Y-%m-%d").date()

		ord_value = Order.objects.filter(order_date__gte = year_start_date,
				order_date__lte = process_end_date,
				user_id = b.user_id).aggregate(sum = Sum('sub_total'))
		total_order_value =0
		if ord_value :
			if ord_value['sum']:
				total_order_value = ord_value['sum']

		###########################################
		##   Determine applicble fee percetnage  ##
		###########################################
		fee_amt = 0
		if total_order_value < 200000:
			perc = 10
		elif total_order_value < 500000:
			perc = 15
		else :
			perc = 20

		total_fee_amt = total_order_value * perc / 100

		#### Orders in last 1 user year for which referral fee is not processed
		orders = Order.objects.filter( order_date__gte = year_start_date,
			order_date__lte = process_end_date,
			user_id = b.user_id )
		
		for o in orders:
		
			##### Skip orders that have payment outstanding
			def_pay = Order_deferred_payment,objects.filter(order = o)
			if not def_pay:
				continue

			##################################################
			## Update referral fee for the order.    		##
			## If order already has a referral fee record	##
			## then update it, else enter new record 		##
			##################################################
			b_ref = Business_referral_fee.objects.filter(order = o).first()
			if b_ref:
				
				bus_ref = Business_referral_fee (
					id = b_ref.id,
					month_year = yrmonth,
					business_profile = b,
					order = o,
					ord_value_ytd = total_order_value,
					fee_amount = o.sub_total * perc / 100,
					fee_paid_date = today,
					fee_paid_reference = '',
					created_date = today,
					updated_date = today
				)
			else:
				bus_ref = Business_referral_fee (
					month_year = yrmonth,
					business_profile = b,
					order = o,
					ord_value_ytd = total_order_value,
					fee_amount = o.sub_total * perc / 100,
					fee_paid_date = today,
					fee_paid_reference = '',
					created_date = today,
					updated_date = today
				)
			
			bus_ref.save()

	return

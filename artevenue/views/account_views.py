from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth import login as auth_login
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings

from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.urls import resolve
from django.contrib import messages
import datetime 

from artevenue.forms import registerForm, businessprofile_Form, businessuserForm
from artevenue.forms import businessprof_Form
from artevenue.forms import userForm, shipping_addressForm, billing_addressForm

from artevenue.models import Pin_code, Business_profile, User_shipping_address
from artevenue.models import User_billing_address, Order, Order_items_view, Cart_item_view

from artevenue.models import Egift, Egift_redemption, User_sms_email
from artevenue.models import Country, State, City, Pin_code

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML, CSS

from .views import *

ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
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

	
def register(request):

	msg =''
	if request.method == 'POST':	
		next = request.POST['curr_pg']
		form = registerForm(request.POST)

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
					'msg':msg} )
		else :	
			if form.is_valid():
				user = form.save()
				auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

				# Update email, sms table
				today = datetime.datetime.today()
				u_email = User_sms_email(
					user = user,
					welcome_email_sent = False,
					welcome_sms_sent = False,
					created_date = today,	
					updated_date = today
				)
				u_email.save()
				# After successful sign up redirect to cuurent page
				return redirect('index')
	else:
		form = registerForm()
	return render(request, "artevenue/register.html", {'form':form} )
	
	
def business_registration(request):

    
	if request.method == 'POST':

		form = businessuserForm(request.POST)
		businessprofile_form = businessprofile_Form(request.POST)

		if form.is_valid():
			if businessprofile_form.is_valid():

				user = form.save()
				auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				# Update email, sms table
				today = datetime.datetime.today()
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
				return render(request, 'artevenue/business_registration_confirm.html', {'form': form, 'businessprofile_form': businessprofile_form})
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
	curruser = get_object_or_404(User, username = request.user)	

	if request.method == 'POST':
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
		'user_form':user_form, 'businessprofile_form':businessprofile_form,
		'shipping_form':shipping_form, 'billing_form':billing_form,
		'egift_giver':egift_giver, 'egift_receiver':egift_receiver,
		'egift_redemption':egift_redemption, 'redemptions':redemptions,
		'country_arr':country_arr, 'state_arr':state_arr,
		'city_arr':city_arr, 'pin_code_arr':pin_code_arr} )


@login_required
def my_orders(request):
	
	return render(request, 'artevenue/my_orders.html')		

@login_required
@csrf_exempt
def get_orders(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")

	user = User.objects.get(username = request.user)
	order_list = Order.objects.filter(user = request.user).order_by('order_number')
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

		html = HTML(string=html_string, base_url=request.build_absolute_uri())
		print(html_string)
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
		'order_shipping').order_by('order_number')
		
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
			'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL})		

'''
@csrf_exempt			
def find_orders(request):
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	order_number = request.POST.get("order_number", '')
	email_id = request.POST.get("email_id", '')

	order_list = Order.objects.filter().select_related('order_billing', 
		'order_shipping').order_by('order_number')
		
	order_items_list = {}
	if email_id:
		pay = Payment_details.objects.filter(email_id = email_id).first().values('order_id')				
		order_list = order_list.filter(order__in = pay)

	if order_number:
		order_list = order_list.filter(order_number = order_number)			

		
	order_items_list = Order_items_view.objects.filter(
		order__in = order_list).select_related('product', 'promotion').values(
		'order_item_id', 'product_id', 'quantity', 'item_total', 'item_sub_total', 'item_tax', 'item_disc_amt',
		'moulding_id', 'item_unit_price', 'product__image_to_frame',
		'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
		'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height',
		'product__thumbnail_url', 'promotion__discount_value', 
		'promotion__discount_type', 'mount__color', 'order_id'
		).order_by('order_id')
	
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
			'startDt':startDt, 'endDt':endDt})

		html = HTML(string=html_string)
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
			'orders': orders, 'order_items_list':order_items_list})							
	'''
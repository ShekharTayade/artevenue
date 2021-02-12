from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q, Max, Sum, F, Avg
from datetime import datetime
import datetime

from django.contrib.auth.models import User

from artevenue.decorators import is_manager
from artevenue.models import Order, Order_items_view, Ecom_site, Business_referral_fee, UserProfile
from artevenue.models import Business_profile
from artevenue.models import Cart, Cart_item_view

from django.contrib.admin.views.decorators import staff_member_required

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

today = datetime.datetime.today()
ecom_site = Ecom_site.objects.get(store_id=settings.STORE_ID )

@csrf_exempt
@is_manager
def get_order_summary(request):
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

	order_list = Order.objects.exclude(order_status = 'CN').order_by('invoice_date')
	
	order_items_list = {}
	if startDt:
		order_list = order_list.filter(order_date__gte = startDt)
	if endDt:
		order_list = order_list.filter(order_date__lte = endDt)
		
	#order_items_list = Order_items_view.objects.filter(
	#	order__in = order_list, product__product_type_id = F('product_type_id')).select_related('product', 'promotion')

	## Totals
	totals = order_list.aggregate(Sum('unit_price'), Sum('quantity'), Sum('order_discount_amt'), 
		Sum('shipping_cost'), Sum('sub_total'), Sum('tax'), Sum('order_total'), Avg('order_total'))

	ord_cnt = order_list.count()


	igst = order_list.exclude(order_billing__state__state_name__iexact=ecom_site.store_state).aggregate(igst=Sum('tax'))
	if igst:
		if igst['igst']:
			total_igst = igst['igst']
		else:
			total_igst = 0.0
	else:
		total_igst = 0.0

	cgst = order_list.filter(order_billing__state__state_name__iexact=ecom_site.store_state).aggregate(cgst=Sum('tax'))
	if cgst :
		if cgst['cgst']:
			total_cgst = cgst['cgst'] / 2
		else:
			total_cgst = 0.0
	else:
		total_cgst = 0.0
		
	total_sgst = total_cgst
	
	if printpdf == "YES":
		html_string = render_to_string('artevenue/order_summary_print.html', {
			'orders': order_list, 'totals':totals, 'startDt':startDt, 'endDt':endDt,
			'ecom_site':ecom_site, 'total_cgst':total_cgst, 'total_sgst':total_sgst,
			'total_igst':total_igst, 'ord_cnt': ord_cnt})

		html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
		
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_ord_pdf.pdf',
			stylesheets=[
						CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
						],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_ord_sum_pdf.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_ord_pdf.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/order_summary_table.html', { 
			'orders': order_list, 'totals':totals, 'startDt':startDt, 'endDt':endDt,
			'ecom_site':ecom_site, 'total_cgst':total_cgst, 'total_sgst':total_sgst,
			'total_igst':total_igst, 'ord_cnt': ord_cnt})


def store_order_summary(request):
	return render(request, 'artevenue/store_order_summary.html')
	
@login_required
def my_business_report_wrap(request):
	
	return render(request, 'artevenue/my_business_report_wrap.html', {})
	

@login_required
@csrf_exempt
def my_business_report(request, user_id=None):
	msg = ''
	business_code = ''
	clients = {}
	client_total = 0
	clients_with_orders = {}
	orders = {}
	total_order_value = 0 
	livaccnt = False
	
	pdf = request.POST.get('printpdf','')
	if pdf == 'TRUE':
		printpdf = True
	else:
		printpdf = False

	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()

	deferred_payment = False
	try:
		if user_id == None:
			username = request.user
			curruser = User.objects.get(username = request.user)
		else:
			curruser = User.objects.get(id = user_id)
		bus_profile = Business_profile.objects.get(user = curruser)
		business_code = bus_profile.business_code
		if business_code == 'LIV1':
			livaccnt = True
		if bus_profile.profile_group:
			deferred_payment = bus_profile.profile_group.deferred_payment
	except Business_profile.DoesNotExist:
		bus_profile = None
		deferred_payment = False
	except User.DoesNotExist:
		curruser = None
	
	if curruser == None:
		msg = "You need to be logged in to view this page"
		return render(request, 'artevenue/my_business_report.html', {'client_total':client_total, 
				'clients_with_orders': clients_with_orders, 'clients':clients, 'orders':orders,
				'total_order_value':total_order_value, 'msg':msg})
	if bus_profile == None:
		msg = "You don't seem to have a business account with us. Please check out 'Business' link at the top of the page."
		return render(request, 'artevenue/my_business_report.html', {'client_total':client_total, 
				'clients_with_orders': clients_with_orders, 'clients':clients, 'orders':orders,
				'total_order_value':total_order_value, 'msg':msg})

	users = UserProfile.objects.filter( business_profile = bus_profile )
	client_ids = UserProfile.objects.filter( business_profile = bus_profile ).values('user_id')
	
	orders = Order.objects.filter( 
			Q( user_id__in = client_ids, order_status = 'PC') | Q( user = curruser, order_status = 'PC' ) 
			| Q( user_id__in = client_ids, order_status = 'IN') | Q( user = curruser, order_status = 'IN' )
			| Q( user_id__in = client_ids, order_status = 'SH') | Q( user = curruser, order_status = 'SH' )
			| Q( user_id__in = client_ids, order_status = 'PR') | Q( user = curruser, order_status = 'PR' )
			| Q( user_id__in = client_ids, order_status = 'CO') | Q( user = curruser, order_status = 'CO' )
			).order_by('user_id')
	if startDt:
		orders = orders.filter(order_date__gte = startDt)
	if endDt:
		orders = orders.filter(order_date__lte = endDt)
	
	clients = User.objects.filter(id__in = client_ids)

	referral = Business_referral_fee.objects.filter( order__in = orders )

	client_total = clients.count()
	clients_with_orders = orders.values('user').distinct().count()
	ord_total = orders.aggregate(ord_amt=Sum('sub_total'))
	total_order_value = ord_total['ord_amt']
	total_fee = referral.aggregate(ref_fee = Sum('fee_amount'))
	total_ref_fee = 0
	if total_fee:
		if total_fee['ref_fee']:
			total_ref_fee = total_fee['ref_fee']

	results = []
	for o in orders:
		row = {}
		ref_fee = 0
		fee_paid_dt = "-"
		fee_paid_ref = ''
		c_email = ''
		def_pay = False
		order_no = o.order_number
		order_date = o.order_date
		order_val = o.sub_total		
		def_pay = o.deferred_payment
		name = ''
		for c in clients:
			if o.user_id == c.id:
				name = c.first_name + ' ' + c.last_name
				c_email = c.email
		for r in referral:
			if o == r.order:
				ref_fee = r.fee_amount
				fee_paid_dt = r.fee_paid_date
				fee_paid_ref = r.fee_paid_reference
		row['id'] = o.order_id
		row['client'] = name
		row['order_number'] = o.order_number
		row['order_date'] = o.order_date
		row['ord_val'] = o.order_total
		row['ord_sub'] = o.sub_total
		row['ref_fee'] = ref_fee
		row['fee_paid_dt'] = fee_paid_dt
		row['fee_paid_ref'] = fee_paid_ref
		row['ref_fee'] = row['deferred_payment'] = def_pay
		row['c_email'] = c_email
		results.append(row)

	if not printpdf :
		return render(request, 'artevenue/my_business_report.html', {'client_total':client_total, 
			'clients_with_orders': clients_with_orders, 'total_order_value':total_order_value, 
			'msg': msg, 'results':results, 'business_code':business_code, 'total_ref_fee':total_ref_fee,
			'livaccnt': livaccnt, 'curruser': curruser, 'startDt': startDt, 'endDt': endDt})
	else:
		html_string = render_to_string('artevenue/my_business_report_pdf.html', {'client_total':client_total, 
			'clients_with_orders': clients_with_orders, 'total_order_value':total_order_value, 
			'msg': msg, 'results':results, 'business_code':business_code, 'total_ref_fee':total_ref_fee,
			'livaccnt': livaccnt, 'curruser': curruser, 'startDt': startDt, 'endDt': endDt})

		html = HTML(string=html_string, base_url=request.build_absolute_uri())
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_business_rep.pdf',
			stylesheets=[CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') ],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_business_rep.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_business_rep.pdf"'
			return response

		return response	

@login_required
def my_client_order_report(request, client_id=None):
	msg = ''
	total_order_value = 0
	orders = {}
	if client_id == None:
		client_id = request.POST.get('client_id', none)
		
	if client_id == None:
		msg = "No client specified"
	
	orders = Order.objects.filter(user_id = client_id).exclude(order_status = 'CN')
	order_total = orders.aggregate(ord_amt = Sum('order_total'))
	if order_total['ord_amt']:
		total_order_value = order_total['ord_amt']
	else:
		total_order_value = 0
	return render(request, 'artevenue/my_client_order_report.html', {
			'orders':orders, 'total_order_value':total_order_value, 'msg': msg}	)


@is_manager			
def cart_order_match_report(request):
	return render(request, 'artevenue/cart_order_sync_report.html')


@csrf_exempt
@is_manager			
def get_cart_order_match(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
	
	## Orders
	orders = Order.objects.filter(order_date__gte = startDt,
		order_date__lte = endDt).exclude(order_number = '').order_by(
		'-order_date')

	count = orders.count()
	
	order_ids = orders.values('order_id')
	order_items = Order_items_view.objects.select_related(
		'product', 'promotion').filter(
		order__in = orders, product__product_type_id = F('product_type_id')).order_by(
		'-order__order_date', 'order_id', 'product__product_id')
	
	order_cart_items_ids = order_items.values('cart_item_id')
	
	cart_ids = orders.values('cart_id')
	carts = Cart.objects.filter( cart_id__in = cart_ids )
	cart_items = Cart_item_view.objects.select_related(
		'product', 'promotion').filter( cart__in = carts,
		product__product_type_id = F('product_type_id') ).order_by(
		'product__product_id')

	n_cart_items = Cart_item_view.objects.select_related(
		'product', 'promotion').filter( cart__in = carts,
		product__product_type_id = F('product_type_id') ).exclude(
		cart_item_id__in = order_cart_items_ids).order_by(
		'product__product_id')
	
	if printpdf == "YES":
		html_string = render_to_string('artevenue/orders_carts_sync_table.html', {
			'orders':order, 'order_items':order_items, 'carts': carts, 
			'cart_items': cart_items, 'startDt': startDt, 'endDt': endDt, 'count': count})

		html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
		
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_ord_pdf.pdf',
			stylesheets=[
						CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
						],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_ord_cart_match.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_ord_cart_match.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/orders_carts_sync_table.html', {
		'orders':orders , 'order_items':order_items, 'carts': carts, 
			'cart_items': cart_items, 'n_cart_items': n_cart_items,
			'startDt': startDt, 'endDt': endDt, 'count': count} )
		
		'''
		'orders':order, 'order_items':order_items, 'carts': carts, 'cart_items': cart_items,
		'startDt': startDt, 'endDt': endDt}	)
		'''
		
		
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

		profile_grp = None
		try:
			profile_grp = Profile_group.objects.get(profile_id = b.profile_group_id)
		except Profile_group.DoesNotExist:
			print("Error Occured: " + b.contact_name + " - " + b.company + ": does not have profile group assigned")
			continue

		############################################################################
		## Process only if it's referral type. If it's a discount type then skip  ##
		############################################################################
		if profile_grp:	
			if profile_type == 'R':			
				## Get clients of this business users	
				clients = UserProfile.objects.filter(business_profile = b)

				if profile_grp.disc_flat == 'F':
					disc_flat = Discount_flat.objects.filter(profile = profile_grp,
						effective_from__lte = process_end_date, 
						effective_from__gte = process_end_date).first()
					disc_perc = disc_flat.voucher.discount_value

				elif profile_grp.disc_flat == 'S':
					slabs = Discount_slab.objects.filter(profile = profile_grp,
						effective_from__lte = process_end_date, 
						effective_from__gte = process_end_date)
				
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
					'''
					ord_value = Order.objects.filter(
							order_date__gte = year_start_date,
							order_date__lte = process_end_date,
							Q(Q(user_id = b.user_id) || Q(user_id__in = client))
							).exclude( order_status = 'CN', order_status = 'PP').aggregate(
								sum = Sum('sub_total'))
						'''
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
						user_id = b.user_id ).exclude(order_status = 'CN')
					
					for o in orders:
					
						##### Skip orders that have payment outstanding
						def_pay = Order_deferred_payment.objects.filter(order = o)
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


@staff_member_required		
def generate_shipping_template(request):
	order_list = Order.objects.filter(order_status = 'SH').select_related('order_billing', 
		'order_shipping').exclude(invoice_number = '').order_by('-updated_date')
	return render(request, 'artevenue/generate_shipping_template.html', {'order_list': order_list})	
	
@staff_member_required		
@csrf_exempt
def get_orders_for_shipping_template(request, order_number=None, printpdf=''):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	order_number = request.POST.get('order_num','')
	invoice_number = request.POST.get('invoice_num', '')
	if printpdf == '':
		printpdf = request.POST.get('printpdf', 'NO')
		
	ordreadyforshippingflag = request.POST.get('ordreadyforshippingflag', 'NO')
	
	if not order_number:
		order_number = request.POST.get("order_number", '')

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")

	if ordreadyforshippingflag == 'NO':
		order_list = Order.objects.filter().select_related('order_billing', 
			'order_shipping').exclude(invoice_number = '').order_by('-updated_date')
		
		order_items_list = {}
		if startDt:
			order_list = order_list.filter(order_date__gte = startDt)
		if endDt:
			order_list = order_list.filter(order_date__lte = endDt)

		if order_number:
			order_list = order_list.filter(order_number = order_number)	

		if invoice_number:
			order_list = order_list.filter(invoice_number = invoice_number)	

		
		if	not startDt and not endDt and not order_number and not invoice_number:
			return render(request, 'artevenue/shipping_template_table.html', { 
				'order_list': {}, 'startDt':startDt, 'endDt':endDt})
				
	## Orders with status ready for shipping
	else:
		order_list = Order.objects.filter(order_status = 'SH').select_related('order_billing', 
			'order_shipping').exclude(invoice_number = '').order_by('-updated_date')
			
	if printpdf == "YES":
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="shipping_template.csv"'
		import csv
		writer = csv.writer(response)
		writer.writerow(['ArteVenue Order Number', 'length', 'width', 'height', 'weight', 'invoice_value', 'description', 
			'insurance', 'billing_address', 'billing_address_postal_code', 'shipper_address', 
			'shipper_address_postal_code', 'shipper_person_name', 'shipper_company_name', 
			'shipper_mobile_number', 'shipper_email', 'receiver_address', 
			'receiver_address_postal_code', 'receiver_person_name', 'receiver_company_name', 
			'receiver_mobile_number', 'receiver_email', 'cod'])

		for order in order_list:
			if order.order_shipping:
				shipping_addrs = order.order_shipping.address_1 + ", " + order.order_shipping.address_2 + ", " + order.order_shipping.land_mark + ", " + order.order_shipping.city + ", " + order.order_shipping.state.state_name	
				shipping_addrs_pin = order.order_shipping.pin_code_id
				s_name = order.order_shipping.full_name
				s_company = order.order_shipping.Company
				s_ph = order.order_shipping.phone_number
				s_email = order.order_shipping.email_id
			else:
				shipping_addrs = shipping_addrs_pin = s_name = s_company = s_ph = s_email = 'N/A'

			row = [order.order_number, '', '', '', '', order.order_total, 'Artwork', 'No', 
				'Montage Art Pvt Ltd, #58 MKR Plaza, JP nagar 1st phase, Sarakki Main road, Bangalore',
				'560078', 'Montage Art Pvt Ltd, #58 MKR Plaza, JP nagar 1st phase, Sarakki Main road, Bangalore',
				'560078', 'Montage Art Pvt Ltd', 'Montage Art Pvt Ltd', '9880337048', 
				'montageframe@gmail.com', shipping_addrs, shipping_addrs_pin, s_name, s_company, 
				s_ph, s_email, 'No']
				
			writer.writerow(row)

		return response		
	else:
		return render(request, 'artevenue/shipping_template_table.html', { 
			'order_list': order_list, 'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL})		

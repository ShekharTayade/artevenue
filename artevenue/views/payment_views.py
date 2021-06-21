from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth import authenticate, login
from django.template import Context, Template,RequestContext
import datetime
import hashlib
from random import randint
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from django.db import IntegrityError, DatabaseError, Error
from decimal import Decimal
from django.db.models import F

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage

from django.template.loader import render_to_string
from django.utils.html import strip_tags
import urllib

from django.core.exceptions import PermissionDenied

from artevenue.models import Order, Order_billing, PrePaymentGateway
from artevenue.models import Payment_details, Cart, Egift, Voucher, Business_profile
from artevenue.models import Voucher_user, Egift_card_design, Voucher_used
from artevenue.models import Order_sms_email, eGift_sms_email, Referral, Order_items_view

MERCHANT_KEY = "ckibPj1d"
key=""
SALT = "hSWhatiYaO"

env = settings.EXEC_ENV

if env == 'DEV' or env == 'TESTING':
	PAYU_BASE_URL = "https://sandboxsecure.payu.in/_payment"  # Testing
	SURL = 'http://localhost:7000/order-confirmation/'
	FURL = 'http://localhost:7000/payment-unsuccessful/'
	CURL = 'http://localhost:7000/payment-unsuccessful/'
	E_SURL = 'http://localhost:7000/egift-payment-done/'
	E_FURL = 'http://localhost:7000/egift-payment-unsuccessful/'
	E_CURL = 'http://localhost:7000/egift-payment-unsuccessful/'
elif env == 'PROD':
	PAYU_BASE_URL = "https://secure.payu.in/_payment "  # LIVE 
	SURL = 'https://artevenue.com/order-confirmation/'
	FURL = 'https://artevenue.com/payment-unsuccessful/'
	CURL = 'https://artevenue.com/payment-unsuccessful/'
	E_SURL = 'https://artevenue.com/egift-payment-done/'
	E_FURL = 'https://artevenue.com/egift-payment-unsuccessful/'
	E_CURL = 'https://artevenue.com/egift-payment-unsuccessful/'
else:
	PAYU_BASE_URL = "https://sandboxsecure.payu.in/_payment"  # Testing
	SURL = 'http://localhost:7000/payment-done/'
	FURL = 'http://localhost:7000/payment-unsuccessful/'
	CURL = 'http://localhost:7000/payment-unsuccessful/'
	E_SURL = 'http://localhost:7000/egift-payment-done/'
	E_FURL = 'http://localhost:7000/egift-payment-unsuccessful/'
	E_CURL = 'http://localhost:7000/egift-payment-unsuccessful/'
		


SERVICE_PROVIDER = 'Montage Art Private Limited'

today = datetime.datetime.today()

def payment_details(request):
	posted={}
	
	order_id = request.POST.get('order_id','')
	for i in request.POST:
		posted[i]=request.POST[i]
		
	order_id = posted['order_id']
	order = Order.objects.get(order_id = order_id)
	
	order_billing = Order_billing.objects.get(order_id = order.order_id)
	
	posted['firstname'] = order_billing.full_name
	posted['lastname'] = order_billing.Company
	posted['amount'] = order.order_total
	posted['email'] = order_billing.email_id
	posted['phone'] = order_billing.phone_number
	posted['productinfo'] = str(order.quantity) + ' items in Order Id: ' + order_id 
	posted['surl'] = SURL
	posted['furl'] = FURL
	posted['service_provider'] = SERVICE_PROVIDER
	posted['curl'] = CURL
	posted['udf1'] = str(order.order_id) 
	posted['udf2'] = str(order.voucher_id)
	posted['udf3'] = str(order.referral_id)
	posted['udf4'] = str(order.order_discount_amt)
	posted['udf6'] = order_billing.Company

	return render (request, 'artevenue/payment_details.html', {"posted":posted,
		'order':order, 'env':env})
		
def payment_submit(request):
	today = datetime.datetime.today()
	posted={}
	for i in request.POST:
		posted[i]=request.POST[i]
		
	order_id = posted['order_id']
	order = Order.objects.get(order_id = order_id)
	
	firstname = posted['firstname']
	
	####################################################################
	## Check if this is a business order. If yes, check if deferred   ##
	## payment is allowed.											  ##
	####################################################################
	bus = None
	deferred_payment = False
	try:
		bus = Business_profile.objects.get( user_id = order.user_id )
	except Business_profile.DoesNotExist: 
		bus = None
	
	if bus:
		if bus.profile_group:
			if bus.profile_group.deferred_payment:
				deferred_payment = True

	cod_flag = False
	if 'cod_val' in posted:
		cod_flag = True
	else:
		cod_flag = False

	if deferred_payment or cod_flag :
		order_items = Order_items_view.objects.select_related(
				'product', 'promotion').filter(
				order = order, product__product_type_id = F('product_type_id'))		
		
		if cod_flag:
			o = Order.objects.filter(order_id = order_id).update(
				order_status = 'PC', deferred_payment = True, order_date = today.date(),
				updated_date = today, payment_type = 'COD')
		
		else:
			o = Order.objects.filter(order_id = order_id).update(
				order_status = 'PC', deferred_payment = True, order_date = today.date(),
				updated_date = today, payment_type = 'ONP')
				
		cart = Cart.objects.filter(cart_id = order.cart_id).update(cart_status = 'CO',
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
			updated_date = today
		)
		o_email.save()
		
		if cod_flag:
			o_template = 'artevenue/order_confirmation_cod.html'
		else:
			o_template = 'artevenue/order_confirmation_deferred_payment.html'

		return render (request, o_template, {"posted":posted,
						'order':order, 'order_items':order_items, 'env':env,
						'firstname': firstname })
	else:
		order_billing = Order_billing.objects.get(order_id = order.order_id)
		##### Firstname, lastname, email and phonenumber are already in the 'posted'
		##### as enetered by user
		posted['amount'] = order.order_total
		posted['productinfo'] = str(order.quantity) + ' items in Order Id: ' + order_id 
		posted['surl'] = SURL
		posted['furl'] = FURL
		posted['service_provider'] = SERVICE_PROVIDER
		posted['curl'] = CURL
		posted['udf1'] = str(order.order_id) 
		posted['udf2'] = str(order.voucher_id)
		posted['udf3'] = str(order.referral_id)
		posted['udf4'] = str(order.order_discount_amt)
		posted['udf6'] = request.POST.get('company','')

		print("Logging pre payment gateway******************")

		try:
			prePay = PrePaymentGateway (
							first_name = posted['firstname'],
							last_name = posted['lastname'],
							phone_number = posted['phone'],
							email_id = posted['email'],
							rec_id = order.order_id,
							date = today,
							amount = order.order_total,
							trn_type = 'ORD'
							)

			prePay.save()
		except Error as e:
			print(e)
		
		hash_object = hashlib.sha256(b'randint(0,20)')
		txnid=hash_object.hexdigest()[0:20]
		hashh = ''
		posted['txnid']=txnid
		hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
		posted['key']=key
		hash_string=''
		hash_string+= MERCHANT_KEY
		
		hashVarsSeq=hashSequence.split('|')
		for i in hashVarsSeq:
			try:
				hash_string+=str(posted[i])
			except Exception:
				hash_string+=''
			hash_string+='|'
		hash_string+=SALT
		hashh=hashlib.sha512(hash_string.encode('utf8')).hexdigest().lower()

		action = PAYU_BASE_URL

		if(posted.get("key")!=None and posted.get("txnid")!=None and posted.get("productinfo")!=None and posted.get("firstname")!=None and posted.get("email")!=None):
			return render (request, 'artevenue/payment_submit.html', {"posted":posted,"hashh":hashh,
							"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
							"action":action, 'env':env })
		else:		
			return render (request, 'artevenue/payment_submit.html', {"posted":posted,"hashh":hashh,
							"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
							"action":".", 'env':env })

@csrf_protect
@csrf_exempt						
def payment_done(request):
	pay_status = "FAIL"
	msg = ''
	c = {}
	c.update(csrf(request))
	today = datetime.datetime.today()
	
	sts = request.POST.get("status","")
	if sts == "":
		raise PermissionDenied

	status=request.POST["status"]
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="GQs7yium"

	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq.encode('utf8')).hexdigest().lower()
	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
		pay_status = "FAIL"
	else:
		pay_status = "PASS"
		print ("Payment passed*****************************")


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''' Let's save the payment details and create the user account '''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	order_total = float(request.POST.get("amount",0))
	order_id = request.POST.get("udf1",'').upper() 
	voucher_id= request.POST.get("udf2",'0')
	referral_id = request.POST.get("udf3",'')
	mode = request.POST.get("mode")
	phone = request.POST.get("phone")
	order_discount_amt = request.POST.get("udf4")	  
	company = request.POST.get("udf6")	  
	email = request.POST.get("email")
	address1 = request.POST.get("address1")
	address2 = request.POST.get("address2")
	city = request.POST.get("city")
	state = request.POST.get("udf5") #For PayUmoney, state is not coming back, so using udf4 for the same
	country = request.POST.get("country")
	zipcode = request.POST.get("zipcode")
	
	try:
		order = Order.objects.get(order_id = order_id)
		
		if order:
			if order.order_status != 'PP' and order.order_status != 'CN' :
				print("==============================================")
				print("Payment info sent again by Payment gateway, do nothing. #" + order.order_number)
				print("==============================================")
				return render(request, "artevenue/estore_base.html",{'env': env})
		
		order_items = Order_items_view.objects.select_related(
				'product', 'promotion').filter(
				order = order, product__product_type_id = F('product_type_id'))		
		
		o = Order.objects.filter(order_id = order_id).update(
			order_status = 'PC', order_date = today.date(),
			updated_date = today)
		cart = Cart.objects.filter(cart_id = order.cart_id).update(cart_status = 'CO',
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
					first_name = firstname,
					last_name = company,
					phone_number = phone,
					email_id = email,
					rec_id = order_id,
					payment_date = datetime.datetime.now(),
					amount = Decimal(amount),
 					payment_txn_status = status,
					payment_txn_id = txnid,
					payment_txn_amount=Decimal(amount),
					payment_txn_posted_hash=posted_hash,
					payment_txn_key=key,
					payment_txn_productinfo=productinfo,
					payment_txn_email=email,
					payment_txn_salt=salt,
					payment_firstname = firstname,
					payment_lastname = company,
					payment_email = email,
					payment_phone = phone,
					payment_address1 = address1,
					payment_address2 = address2,
					payment_city = city,
					payment_state = state,
					payment_country = country,
					payment_zip_code = zipcode,
					trn_type = 'ORD'
					
				)

		paymnt.save()
		
		db_err = 'PASS'
		if order.user:
			user = order.user
			#user = authenticate(request, email=email, username=username, password=password)
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
		
	except Error as e:
		msg = 'Apologies!! Could not record your payment. Not to worry though. Our team will have your payment and order confirmed. Please feel free to contact us at support@artevenue.com' + (e.message)
		db_err = 'FAIL'
		print ("Error:************************")
		print ( '%s (%s)' % (e.message, type(e)) )
		
	return render(request, 'artevenue/payment_done.html',
			{ "txnid":txnid, "status":status, "amount":amount, 'msg':msg,
			'db_err':db_err, 'firstname':firstname, 'order':order,
			'pay_status':pay_status, 'order_items':order_items,'env': env }
		)


@csrf_protect
@csrf_exempt						
def payment_unsuccessful(request):
	pay_status = "FAIL"
	msg = ''
	c = {}
	c.update(csrf(request))
	today = datetime.datetime.today()
	
	status=request.POST["status"]
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="GQs7yium"

	
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq.encode('utf8')).hexdigest().lower()
	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
		pay_status = "FAIL"
	else:
		pay_status = "PASS"
		print ("Payment passed*****************************")


	order_total = float(request.POST.get("amount",0))
	order_id = request.POST.get("udf1",'').upper() 
	voucher_id= request.POST.get("udf2",'0')
	referral_id = request.POST.get("udf3",'')
	mode = request.POST.get("mode")
	phone = request.POST.get("phone")
	order_discount_amt = request.POST.get("udf4")	  
	company = request.POST.get("udf6")	  
	email = request.POST.get("email")
	address1 = request.POST.get("address1")
	address2 = request.POST.get("address2")
	city = request.POST.get("city")
	state = request.POST.get("udf5") #For PayUmoney, state is not coming back, so using udf4 for the same
	country = request.POST.get("country")
	zipcode = request.POST.get("zipcode")
		
	order = Order.objects.get(order_id = order_id)

	if order.user:
		user = order.user
		#user = authenticate(request, email=email, username=username, password=password)
		login(request, user, backend='django.contrib.auth.backends.ModelBackend')

	return render(request, 'artevenue/payment_unsuccessful.html',
			{ "txnid":txnid, "status":status, "amount":amount, 'msg':msg,
			'firstname':firstname, 'order':order,
			'pay_status':pay_status, 'env':env}
		)	
			
def egift_payment_details(request):
	posted={}
	
	gift_rec_id = request.POST.get('gift_rec_id','')
	egift = Egift.objects.get(gift_rec_id = gift_rec_id)
	
	posted['firstname'] = egift.giver.first_name
	posted['lastname'] = egift.giver.last_name
	posted['amount'] = egift.gift_amount
	posted['email'] = egift.giver.email
	posted['phone'] = ''
	posted['productinfo'] = "Arte'Venue.com eGift Card: Rs. " + str(egift.gift_amount)
	posted['surl'] = SURL
	posted['furl'] = FURL
	posted['service_provider'] = SERVICE_PROVIDER
	posted['curl'] = CURL
	posted['udf1'] = str(egift.gift_rec_id) 
	posted['udf2'] = egift.giver.last_name

	return render (request, 'artevenue/egift_payment_details.html', {"posted":posted,
		'egift':egift})


def egift_payment_submit(request):
	posted={}
	today = datetime.datetime.today()
	
	for i in request.POST:
		posted[i]=request.POST[i]
		
	gift_rec_id = posted['gift_rec_id']
	egift = Egift.objects.get(gift_rec_id = gift_rec_id)
	
	##### Firstname, lastname, email and phonenumber are already in the 'posted'
	##### as enetered by user
	posted['amount'] = egift.gift_amount
	posted['productinfo'] = "Arte'Venue.com eGift Card: Rs. " + str(egift.gift_amount)
	posted['surl'] = E_SURL
	posted['furl'] = E_FURL
	posted['service_provider'] = SERVICE_PROVIDER
	posted['curl'] = E_CURL
	posted['udf1'] = str(egift.gift_rec_id) 
	posted['udf2'] = egift.giver.last_name 

	try:
		prePay = PrePaymentGateway (
						first_name = posted['firstname'],
						last_name = posted['lastname'],
						phone_number = posted['phone'],
						email_id = posted['email'],
						rec_id = egift.gift_rec_id,
						date = today,
						amount = egift.gift_amount,
						trn_type = 'GFT'
						)

		prePay.save()
	except Error as e:
		print(e)
	
	hash_object = hashlib.sha256(b'randint(0,20)')
	txnid=hash_object.hexdigest()[0:20]
	hashh = ''
	posted['txnid']=txnid
	hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
	posted['key']=key
	hash_string=''
	hash_string+= MERCHANT_KEY
	
	hashVarsSeq=hashSequence.split('|')
	for i in hashVarsSeq:
		try:
			hash_string+=str(posted[i])
		except Exception:
			hash_string+=''
		hash_string+='|'
	hash_string+=SALT
	hashh=hashlib.sha512(hash_string.encode('utf8')).hexdigest().lower()

	action = PAYU_BASE_URL

	if(posted.get("key")!=None and posted.get("txnid")!=None and posted.get("productinfo")!=None and posted.get("firstname")!=None and posted.get("email")!=None):
		return render (request, 'artevenue/egift_payment_submit.html', {"posted":posted,"hashh":hashh,
						"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
						"action":action })
	else:		
		return render (request, 'artevenue/egift_payment_submit.html', {"posted":posted,"hashh":hashh,
						"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
						"action":"." })

		
@csrf_protect
@csrf_exempt						
def egift_payment_done(request):
	today = datetime.datetime.today()
	pay_status = "FAIL"
	msg = ''
	c = {}
	c.update(csrf(request))
	
	status=request.POST["status"]
	firstname=request.POST["firstname"]
	gift_amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="GQs7yium"
	
	
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+gift_amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+gift_amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq.encode('utf8')).hexdigest().lower()
	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
		pay_status = "FAIL"
	else:
		pay_status = "PASS"


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''' Let's save the payment details and create the user account '''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	gift_amount = float(request.POST.get("amount",0))
	gift_rec_id = request.POST.get("udf1",'') 
	lastname = request.POST.get("udf2",'') 
	mode = request.POST.get("mode")
	phone = request.POST.get("phone")
	email = request.POST.get("email")
	address1 = request.POST.get("address1")
	address2 = request.POST.get("address2")
	city = request.POST.get("city")
	state = request.POST.get("udf5") #For PayUmoney, state is not coming back, so using udf4 for the same
	country = request.POST.get("country")
	zipcode = request.POST.get("zipcode")

	try:
		egift = Egift.objects.get(gift_rec_id = gift_rec_id)
		
		# Save the registration, subscription, payment, promotion code details 
		paymnt = Payment_details(
					first_name = egift.giver.first_name,
					last_name = egift.giver.last_name,
					phone_number = phone,
					email_id = egift.giver.email,
					rec_id = gift_rec_id,
					payment_date = datetime.datetime.now(),
					amount = Decimal(gift_amount),
 					payment_txn_status = status,
					payment_txn_id = txnid,
					payment_txn_amount=Decimal(gift_amount),
					payment_txn_posted_hash=posted_hash,
					payment_txn_key=key,
					payment_txn_productinfo=productinfo,
					payment_txn_email=email,
					payment_txn_salt=salt,
					payment_firstname = firstname,
					payment_lastname = lastname,
					payment_email = email,
					payment_phone = phone,
					payment_address1 = address1,
					payment_address2 = address2,
					payment_city = city,
					payment_state = state,
					payment_country = country,
					payment_zip_code = zipcode,
					trn_type = 'GFT'
				)
		paymnt.save()
	
		
		# Update the egift transaction
		e = Egift.objects.filter(gift_rec_id = gift_rec_id).update(
			payment_status = 'PC')

		################################
		#Create the eGift coupan/voucher
		################################
		import uuid
		voucher_code = uuid.uuid4().hex[:8].upper()

		# Make sure generated code is not already used
		voucher_exist = Voucher.objects.filter(voucher_code = voucher_code)
		while voucher_exist:
			voucher_code = uuid.uuid4().hex[:8].upper()
			voucher_exist = Voucher.objects.filter(voucher_code = voucher_code)
			
		voucher = Voucher(
			voucher_code = voucher_code,
			store_id = settings.STORE_ID,
			effective_from = today,
			effective_to = today.replace(year=today.year + 1),
			discount_type = 'CASH',
			discount_value = Decimal(gift_amount),
			all_applicability = False,
			created_date = today,	
			updated_date = today
		)
		voucher.save()
		
		# Update eGift with created voucher
		e = Egift.objects.filter(gift_rec_id = gift_rec_id).update(
			voucher = voucher)		
			
		egift_email_sms = eGift_sms_email (
			egift_id = gift_rec_id,
			receiver_email_sent = False,
			giver_email_sent = False,
			receiver_sms_sent = False,
			giver_sms_sent = False,
			created_date = today,
			updated_date = today
			)			
		egift_email_sms.save()
		
		# Check if receiver already has a login, if yes created the voucher user
		# otherwise voucher user is to be crated whenever someone signs up with
		# the receiver email id
		receiver = User.objects.filter(email = egift.receiver_email).first()
		if receiver:
			voucher_user = Voucher_user(
				voucher = voucher,
				user = receiver,
				effective_from = voucher.effective_from,
				effective_to = voucher.effective_to,
				used_date = None,
				created_date = today,
				updated_date = today,
			)
			voucher_user.save()
			'''
			if egift.delivery_date <= today.date():
				# Send email to receiver
				subject = "A Gift for you from: " + egift.giver.first_name + " " + egift.giver.last_name + " (" + egift.giver.email + ")"
				html_message = render_to_string('artevenue/voucher_email.html', 
						{'voucher': voucher, 'voucher_user':voucher_user, 'egift':egift})
				plain_message = strip_tags(html_message)
				from_email = 'support@artevenue.com'
				to = voucher_user.user.email
				emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
				emsg.attach_alternative(html_message, "text/html")
				emsg.send()				
			
				# Send email to giver
				subject = "Your eGift card delivered to: " + egift.receiver.first_name + " " + egift.receiver.last_name + " (" + egift.receiver.email + ")"
				html_message = render_to_string('artevenue/voucher_sent_email.html', 
						{'voucher': voucher, 'voucher_user':voucher_user, 'egift':egift})
				plain_message = strip_tags(html_message)
				from_email = 'support@artevenue.com'
				to = egift.giver.email
				emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
				emsg.attach_alternative(html_message, "text/html")
				emsg.send()				
			'''
		db_err = 'PASS'
		
		
	except Error as e:
		print(e)
		msg = 'Apologies!! Could not record the gift transaction. Not to worry though. Our team will have your payment and gift order confirmed. Please feel free to contact us at support@artevenue.com'
		db_err = 'FAIL'

		
	return render(request, 'artevenue/egift_payment_done.html',
			{ "txnid":txnid, "status":status, "amount":gift_amount, 'msg':msg,
			'db_err':db_err, 'firstname':firstname, 'egift':egift,
			'pay_status':pay_status}
		)

@csrf_protect
@csrf_exempt						
def egift_payment_unsuccessful(request):
	today = datetime.datetime.today()
	pay_status = "FAIL"
	msg = ''
	c = {}
	c.update(csrf(request))

	status=request.POST["status"]
	firstname=request.POST["firstname"]
	gift_amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="GQs7yium"
	
	
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+gift_amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+gift_amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq.encode('utf8')).hexdigest().lower()
	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
		pay_status = "FAIL"
	else:
		pay_status = "PASS"


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''' Let's save the payment details and create the user account '''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	gift_amount = float(request.POST.get("amount",0))
	gift_rec_id = request.POST.get("udf1",'') 
	lastname = request.POST.get("udf2",'') 
	mode = request.POST.get("mode")
	phone = request.POST.get("phone")
	email = request.POST.get("email")
	address1 = request.POST.get("address1")
	address2 = request.POST.get("address2")
	city = request.POST.get("city")
	state = request.POST.get("udf5") #For PayUmoney, state is not coming back, so using udf4 for the same
	country = request.POST.get("country")
	zipcode = request.POST.get("zipcode")

	egift = Egift.objects.get(gift_rec_id = gift_rec_id)
	
		
	return render(request, 'artevenue/egift_payment_unsuccessful.html',
			{ "txnid":txnid, "status":status, "amount":gift_amount, 'msg':msg,
			'db_err':db_err, 'firstname':firstname, 'egift':egift,
			'pay_status':pay_status}
		)
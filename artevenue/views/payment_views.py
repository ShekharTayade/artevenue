from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context, Template,RequestContext
import datetime
import hashlib
from random import randint
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from django.db import IntegrityError, DatabaseError, Error

from artevenue.models import Order, Order_billing, PrePaymentGateway
from artevenue.models import Payment_details, Cart, Egift

MERCHANT_KEY = "ckibPj1d"
key=""
SALT = "hSWhatiYaO"
PAYU_BASE_URL = "https://sandboxsecure.payu.in/_payment"  # Testing
###PAYU_BASE_URL = "https://secure.payu.in/_payment "  # LIVE 
SURL = 'http://www.artevenue.com/payment_done/'
FURL = 'http://www.artevenue.com/payment_unsuccessful/'
CURL = 'http://www.artevenue.com/payment_unsuccessful/'
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
		'order':order})
		
def payment_submit(request):
	posted={}
	for i in request.POST:
		posted[i]=request.POST[i]
		
	order_id = posted['order_id']
	order = Order.objects.get(order_id = order_id)
	
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
						"action":action })
	else:		
		return render (request, 'artevenue/payment_submit.html', {"posted":posted,"hashh":hashh,
						"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
						"action":"." })

@csrf_protect
@csrf_exempt						
def payment_done(request):
	pay_status = "FAIL"
	msg = ''
	c = {}
	c.update(csrf(request))
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
		o = Order.objects.filter(order_id = order_id).update(
			order_status = 'PC', order_date = today.date(),
			updated_date = today)
		cart = Cart.objects.filter(cart_id = order.cart_id).update(cart_status = 'CO',
			updated_date = today)
		
		# Save the registration, subscription, payment, promotion code details 
		paymnt = Payment_details(
					first_name = firstname,
					last_name = company,
					phone_number = phone,
					email_id = email,
					rec_id = order_id,
					payment_date = datetime.datetime.now(),
					amount = amount,
 					payment_txn_status = status,
					payment_txn_id = txnid,
					payment_txn_amount=amount,
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
		
		
	except Error as e:
		msg = 'Apologies!! Could not record your payment. Not to worry though. Our team will have your payment and order confirmed. Please feel free to contact us at support@artevenue.com'
		db_err = 'FAIL'

		
	return render(request, 'artevenue/payment_done.html',
			{ "txnid":txnid, "status":status, "amount":amount, 'msg':msg,
			'db_err':db_err, 'firstname':firstname, 'order':order,
			'pay_status':pay_status}
		)


def eGift_payment_details(request):
	posted={}
	
	gift_rec_id = request.POST.get('gift_rec_id','')
	egift = Egift.objects.get(gift_rec_id = gift_rec_id)
	
	posted['firstname'] = egift.user.firstname
	posted['lastname'] = egift.user.lastname
	posted['amount'] = egift.gift_amount
	posted['email'] = egift.user.email
	posted['phone'] = egift.user.phone_number
	posted['productinfo'] = "Arte'Venue.com eGift Card: Rs. " + egift.gift_amount 
	posted['surl'] = SURL
	posted['furl'] = FURL
	posted['service_provider'] = SERVICE_PROVIDER
	posted['curl'] = CURL
	posted['udf1'] = str(egift.gift_rec_id) 
	posted['udf2'] = str(egift.gift_rec_id) 

	return render (request, 'artevenue/egift_payment_details.html', {"posted":posted,
		'egift':egift})


def egift_payment_submit(request):
	posted={}
	for i in request.POST:
		posted[i]=request.POST[i]
		
	gift_rec_id = posted['gift_rec_id']
	egift = Order.objects.get(gift_rec_id = gift_rec_id)
	
	##### Firstname, lastname, email and phonenumber are already in the 'posted'
	##### as enetered by user
	posted['amount'] = egift.gift_amount
	posted['productinfo'] = "Arte'Venue.com eGift Card: Rs. " + egift.gift_amount 
	posted['surl'] = SURL
	posted['furl'] = FURL
	posted['service_provider'] = SERVICE_PROVIDER
	posted['curl'] = CURL
	posted['udf1'] = str(egift.gift_rec_id) 
	posted['udf2'] = str(egift.gift_rec_id) 

	try:
		prePay = PrePaymentGateway (
						first_name = posted['firstname'],
						last_name = posted['lastname'],
						phone_number = posted['phone'],
						email_id = posted['email'],
						rec_id = egift.gift_rec_id,
						date = today,
						amount = order.order_total,
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
		return render (request, 'artevenue/payment_submit.html', {"posted":posted,"hashh":hashh,
						"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
						"action":action })
	else:		
		return render (request, 'artevenue/payment_submit.html', {"posted":posted,"hashh":hashh,
						"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
						"action":"." })

		
@csrf_protect
@csrf_exempt						
def egift_payment_done(request):
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
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
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
					first_name = egift.user.firstname,
					last_name = egift.user.lastname,
					phone_number = phone,
					email_id = egift.user.email,
					rec_id = gift_rec_id,
					payment_date = datetime.datetime.now(),
					amount = gift_amount,
 					payment_txn_status = status,
					payment_txn_id = txnid,
					payment_txn_amount=gift_amount,
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
					trn_type = 'EGF'
					
				)

		paymnt.save()
		db_err = 'PASS'
		
		
	except Error as e:
		msg = 'Apologies!! Could not record your payment. Not to worry though. Our team will have your payment and order confirmed. Please feel free to contact us at support@artevenue.com'
		db_err = 'FAIL'

		
	return render(request, 'artevenue/egift_payment_done.html',
			{ "txnid":txnid, "status":status, "amount":amount, 'msg':msg,
			'db_err':db_err, 'firstname':firstname, 'egift':egift,
			'pay_status':pay_status}
		)

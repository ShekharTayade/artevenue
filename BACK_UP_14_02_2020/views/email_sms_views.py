from django.shortcuts import render, get_object_or_404
import datetime
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template.context_processors import csrf
from django.db import IntegrityError, DatabaseError, Error
from decimal import Decimal
from django.db.models import F
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.templatetags.static import static

from django.template.loader import render_to_string
from django.utils.html import strip_tags

import urllib
from PIL import ImageFont, ImageDraw, Image

from django.contrib.auth.models import User

from artevenue.models import Order, Order_items_view, Publisher, Egift_card_design
from artevenue.models import Voucher, eGift_sms_email, Egift, Voucher_user, Cart
from artevenue.models import Order_sms_email, Order_shipping, Order_billing
from artevenue.models import Business_profile, User_sms_email, Contact_us, Cart_item_view

today = datetime.datetime.today()
cc = "support@artevenue.com"

def send_customer_emails():
	# Select orders where customer emails not sent	
	err_flag = False
	mail_cnt = 0

	cust_orders = Order_sms_email.objects.filter(
		customer_email_sent = False).values('order_id')
	
	
	orders = Order.objects.filter(order_id__in = cust_orders)
	order_ids = Order.objects.filter(order_id__in = cust_orders).values('order_id')
	order_items_list = Order_items_view.objects.select_related('product').filter(order_id__in = order_ids,
		product__product_type_id = F('product_type_id'))
	
	for o in orders:
		#get email id from Order_shipping
		ord_shp = Order_shipping.objects.get(order = o)
		if ord_shp:
			to = ord_shp.email_id
		else:
			#get email id from Order_shipping
			ord_bill = Order_billing.objects.get(order = o)
			to = ord_bill.email_id
			if not ord_bill:	
				err_flag = True
				print('Customer email ID not found in shipping or billing address')

		if not err_flag:
		
			#############################
			## Send email to customer
			#############################
			subject = "ArteVenue.com Order No.: " + o.order_number
			html_message = render_to_string('artevenue/customer_order_email.html', 
					{'order': o, 'order_items_list':order_items_list,
					'MEDIA_URL':settings.MEDIA_URL})
			plain_message = strip_tags(html_message)
			from_email = 'support@artevenue.com'
		
			emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to], [cc])
			emsg.attach_alternative(html_message, "text/html")
			emsg.send()	
			# Update email sent status
			cust_o = Order_sms_email.objects.filter(order = o)
			cust_o.update(customer_email_sent = True, updated_date=today)
			mail_cnt = mail_cnt + 1

	return (mail_cnt)
	

def send_factory_emails():
	# Select orders where customer emails not sent	
	err_flag = False
	mail_cnt = 0

	factory_orders = Order_sms_email.objects.filter(
		factory_email_sent = False).values('order_id')

	orders = Order.objects.filter(order_id__in = factory_orders)
	order_ids = Order.objects.filter(order_id__in = factory_orders).values('order_id')
	order_items_list = Order_items_view.objects.select_related('product').filter(order_id__in = order_ids,
		product__product_type_id = F('product_type_id'))

	publ = Publisher.objects.all()

	to = 'factory@artevenue.com'
	for o in orders:
		#############################
		## Send email to factory
		#############################
		subject = "ArteVenue.com Order No.: " + o.order_number
		html_message = render_to_string('artevenue/factory_order_email.html', 
				{'order': o, 'order_items_list':order_items_list, 
				'base':settings.BASE_DIR, 'publ':publ, 'MEDIA_URL':settings.MEDIA_URL})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to], [cc])
		emsg.attach_alternative(html_message, "text/html")
		for ol in order_items_list:
			if o.order_id == ol.order_id:
				# Get Image file, if it's user uploaded file
				user_image_url = ''
				if ol.product_type_id == 'USER-IMAGE':
					user_image_url = settings.PROJECT_DIR + ol.product.image_to_frame.url
					if user_image_url:
						emsg.attach_file(user_image_url)
		emsg.send()	
		# Update email sent status
		fact_o = Order_sms_email.objects.filter(order = o)
		fact_o.update(factory_email_sent = True, updated_date=today)
		mail_cnt = mail_cnt + 1

	return (mail_cnt)

def send_egift_emails():
	# Select orders where customer emails not sent	
	err_flag = False
	mail_cnt = 0
	#f = settings.EGIFT_DESIGNS + egift.egift_card_design.url
	card_folder = 'static/img/'

	egift_ids = eGift_sms_email.objects.filter(
		receiver_email_sent = False).values('egift')	
	
	egifts = Egift.objects.filter(gift_rec_id__in = egift_ids)

	for egift in egifts:
		if egift.delivery_date <= today.date():

			##################################################
			# Create card design
			##################################################			
			egift_card_design = Egift_card_design.objects.get(design_id = egift.egift_card_design_id)
			##################################
			# Get the voucher
			##################################
			voucher = Voucher.objects.get(voucher_id = egift.voucher_id)
			voucher_user = Voucher_user.objects.filter(voucher = voucher, 
				used_date__isnull = True).first()
			print(voucher.voucher_code)
			img_path = settings.EGIFT_DESIGNS + egift.egift_card_design.url

			card_img=Image.open(img_path)
			img_save_location = settings.STATIC_ROOT + '/egift_cards/' + str(egift.gift_rec_id) + '.jpg'
			img_url = 'http://artevenue.com/static/egift_cards/' + str(egift.gift_rec_id) + '.jpg'

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
		
			print("eGift Order No: " + str(egift.gift_rec_id))
			#get email id of receiver
			to = egift.receiver_email

			
			#############################
			## Send email to receiver
			#############################
			subject = "You have gift from " + egift.giver.first_name + " " + egift.giver.last_name
			html_message = render_to_string('artevenue/voucher_email.html', 
				{'egift': egift, 'voucher':voucher, 'card_folder':card_folder,
				'img_url':img_url})
			plain_message = strip_tags(html_message)
			from_email = 'support@artevenue.com'
		
			emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to], [cc])
			emsg.attach_alternative(html_message, "text/html")
			print("sending email to receiver: " + to)
			emsg.send()	
			# Update email sent status
			egift_r = eGift_sms_email.objects.filter(
				egift_id = egift.gift_rec_id).update(
					receiver_email_sent = True)
			#Update the eGift with datetime
			eg = Egift.objects.filter(gift_rec_id = egift.gift_rec_id).update(
					receiver_email_sent = today, updated_date=today)
				
			print("Email sent to: " + to)
			mail_cnt = mail_cnt + 1

	## GIVER
	egift_ids = eGift_sms_email.objects.filter(
		giver_email_sent = False).values('egift')		
	egifts = Egift.objects.filter(gift_rec_id__in = egift_ids)
	for egift in egifts:
		##################################################
		# Create card design
		##################################################			
		##################################
		# Get the voucher
		##################################
		voucher = Voucher.objects.get(voucher_id = egift.voucher_id)
		voucher_user = Voucher_user.objects.filter(voucher = voucher, 
			used_date__isnull = True).first()
		print(voucher.voucher_code)
		egift_card_design = Egift_card_design.objects.get(design_id = egift.egift_card_design_id)
		img_path = settings.EGIFT_DESIGNS + egift.egift_card_design.url

		card_img=Image.open(img_path)
		img_save_location = settings.STATIC_ROOT + '/egift_cards/' + str(egift.gift_rec_id) + '.jpg'
		img_url = 'http://artevenue.com/static/egift_cards/' + str(egift.gift_rec_id) + '.jpg'

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

	
		print("eGift Order No: " + str(egift.gift_rec_id))
		#get email id of receiver
		to = egift.giver.email

		# Get the voucher
		voucher = Voucher.objects.get(voucher_id = egift.voucher_id)
		print(voucher.voucher_code)

		#############################
		## Send email to giver
		#############################
		subject = "You have sent gift to " + egift.receiver_name
		html_message = render_to_string('artevenue/voucher_email_giver.html', 
			{'egift': egift, 'voucher':voucher, 'card_folder':card_folder,
			'img_url':img_url})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to], [cc])
		emsg.attach_alternative(html_message, "text/html")
		print("sending email to giver: " + to)
		emsg.send()	
		# Update email sent status
		egift_r = eGift_sms_email.objects.filter(
			egift_id = egift.gift_rec_id).update(
				giver_email_sent = True)
		#Update the eGift with datetime
		eg = Egift.objects.filter(gift_rec_id = egift.gift_rec_id).update(
				giver_email_sent = today, updated_date=today)
		mail_cnt = mail_cnt + 1

	return (mail_cnt)


def send_business_account_approval_email(request, id):
	
	accnt = get_object_or_404(Business_profile, pk=id)
	
	if accnt:
		to = accnt.user.email
		subject = "You business account is active. Welcome on board Arte'Venue!"
		html_message = render_to_string('artevenue/business_account_approval_email.html', 
			{'accnt': accnt})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to], [cc])
		emsg.attach_alternative(html_message, "text/html")
		print("sending email to: " + accnt.contact_name + ", " + accnt.company)
		emsg.send()	
	return
	
def new_customer_emails():
	users = User_sms_email.objects.filter( welcome_email_sent = False )
	mail_cnt = 0
	for u in users:
		## Check if it's a busines user
		business_user = Business_profile.objects.filter(user = u.user).first()
		if business_user:
			template = 'artevenue/new_business_customer_email.html'
		else:
			template = 'artevenue/new_customer_email.html'
			
		to = u.user.email
		subject = "Welcome on board Arte'Venue!"
		html_message = render_to_string(template, 
			{'user': u.user, 'business_user':business_user})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to], [cc])
		emsg.attach_alternative(html_message, "text/html")
		print("sending email to: " + u.user.email)
		emsg.send()	
		mail_cnt = 	mail_cnt + 1
		user_email = User_sms_email.objects.filter(user_id = u.user_id).update(
			welcome_email_sent = True, updated_date=today)

	return mail_cnt


def send_contact_us_emails():
	# Select orders where customer emails not sent	
	err_flag = False
	mail_cnt = 0

	contacts = Contact_us.objects.filter(
		email_sent_to_artevenue = False).order_by('msg_datetime')
	
	for c in contacts:
		name = c.first_name + ' ' + c.last_name
		subject = "Message from user a through Website-Contact Us form"
		html_message = render_to_string('artevenue/contact_us_form_email_to_artevenue.html', 
				{'contact_form': c, 'name':name})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
		to = 'support@artevenue.com'
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to], [cc])
		emsg.attach_alternative(html_message, "text/html")
		emsg.send()	
		# Update email sent status
		c_f = Contact_us.objects.filter(pk = c.id).update(email_sent_to_artevenue = True)
		mail_cnt = mail_cnt + 1

	return (mail_cnt)
	
def send_carts_with_order_without_payment():	

	cart_list = Cart.objects.filter(cart_status = 'AC').order_by('-updated_date')
	cart_list_cust = Cart.objects.filter(cart_status = 'AC', user__isnull = False).order_by('-updated_date')
	ord = []
	cart_items = {}
	for c in cart_list:
		ord = Order.objects.filter( cart_id = c.cart_id).first()
		if ord:
			if ord.order_status != 'PP':
				cart_list = cart_list.exclude(cart_id = c.cart_id)
			## for Signed up customer, no orders
			cart_list_cust = cart_list.exclude(cart_id = c.cart_id)			
		else:
			cart_list = cart_list.exclude(cart_id = c.cart_id)
			
			
		cart_items = Cart_item_view.objects.select_related('product').filter(
						cart__in = cart_list, product__product_type_id = F('product_type_id'))

	orders = Order.objects.filter( cart__in = cart_list)

	if cart_list:
		subject = "ArteVenue.com: Carts with checkout, payment not done"
		hd = "Customer cart details (checked out but payment not done)"
		html_message = render_to_string('artevenue/carts_with_ord_without_payment.html', 
				{'cart_list': cart_list, 'cart_items':cart_items, 'orders':orders, 'today':today,
				'hd':hd})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
		#to = ['prash@bizinventive.com', 'anu@bizinventive.com']
		#cc = ['shekhar@artevenue.com', 'neeraj@artevenue.com']
		to = ['shekhart@hotmail.com']
		cc = ['']
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, to, cc)
		emsg.attach_alternative(html_message, "text/html")
		emsg.send()	


def send_orders_no_payment():	

	order_billing = Order_billing.objects.filter(order__order_status = 'PP')
	ord_bill_ids = order_billing.values('order_id')
	ordlist = Order.objects.filter(order_id__in = ord_bill_ids).values('cart_id')
	carts = Cart.objects.filter (cart_id__in = ordlist)

	cart_items = Cart_item_view.objects.select_related('product').filter(
						cart__in = carts, product__product_type_id = F('product_type_id'))

	if order_billing:
		subject = "ArteVenue.com: Checked out carts, Order not placed"
		hd = "Checked out carts (Order not placed)"
		html_message = render_to_string('artevenue/checkedout_carts_no_order.html', 
				{'order_billing':order_billing, 'today':today, 'cart_items':cart_items,
				'hd':hd})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
		to = ['prash@bizinventive.com', 'anu@bizinventive.com']
		cc = ['shekhar@artevenue.com', 'neeraj@artevenue.com']
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, to, cc)
		emsg.attach_alternative(html_message, "text/html")
		emsg.send()

	
def offer_for_users_with_unused_coupan():

	v_user_ids = Cart.objects.filter(voucher_id = 8).values('user_id')
	v_ord_users = Order.objects.filter(user_id__in = v_user_ids, voucher_id = 8).values('user_id').exclude(order_status = 'PP')
	carts = Cart.objects.filter(voucher_id = 8).exclude(user_id__in = v_ord_users)
	
	for cart_list in carts:
		cart_items = Cart_item_view.objects.filter(cart_id = cart_list.cart_id)	
		subject = "A New Year offer from ArteVenue.com"
		html_message = render_to_string('artevenue/offer_for_users_with_unused_coupan.html', 
				{'cart_list':cart_list, 'cart_items':cart_items})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
		to = ['shekhar@artevenue.com']
		cc = ['']

		emsg = EmailMultiAlternatives(subject, plain_message, from_email, to, cc)
		emsg.attach_alternative(html_message, "text/html")
		emsg.send()


def offer_25():
	user = User.objects.all()

	for u in user:
		cart = Cart.objects.filter(user = u, cart_status = 'AC').first()
		if cart:
			cart_items = Cart_item_view.objects.select_related('product').filter(
							cart_id = cart.cart_id, product__product_type_id = F('product_type_id'))
		else:
			cart_items = {}
		subject = "Hello " + u.first_name + " " + u.last_name + ", A New Year offer for you from Arte'Venue, a flat 25% off"
		html_message = render_to_string('artevenue/offer_25.html', 
				{'user':u, 'cart_items':cart_items})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
		to = [u.email]
		cc = ['shekhar@artevenue.com']

		emsg = EmailMultiAlternatives(subject, plain_message, from_email, to, cc)
		emsg.attach_alternative(html_message, "text/html")
		emsg.send()	
	
	
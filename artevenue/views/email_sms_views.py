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

from artevenue.models import Order, Order_items_view, Publisher, Egift_card_design
from artevenue.models import Voucher, eGift_sms_email, Egift, Voucher_user
from artevenue.models import Order_sms_email, Order_shipping, Order_billing
from artevenue.models import Business_profile, User_sms_email

today = datetime.datetime.today()
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
		
			emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
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
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
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
		
			emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
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
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
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
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
		emsg.attach_alternative(html_message, "text/html")
		print("sending email to: " + accnt.contact_name + ", " + accnt.company)
		emsg.send()	
	return
	
def new_customer_emails():
	users = User_sms_email.objects.filter( welcome_email_sent = False )
	mail_cnt = 0
	for u in users:
		to = u.user.email
		subject = "Welcome on board Arte'Venue!"
		html_message = render_to_string('artevenue/new_customer_email.html', 
			{'user': u.user})
		plain_message = strip_tags(html_message)
		from_email = 'support@artevenue.com'
	
		emsg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
		emsg.attach_alternative(html_message, "text/html")
		print("sending email to: " + u.user.email)
		emsg.send()	
		mail_cnt = 	mail_cnt + 1
		user_email = User_sms_email.objects.filter(user_id = u.user_id).update(
			welcome_email_sent = True, updated_date=today)

	return mail_cnt
		
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models import Count, Q, Max, Sum
from decimal import Decimal

from datetime import datetime
import datetime
from decimal import Decimal
import json
from django.http import HttpRequest

from artevenue.models import Cart, Stock_image, User_image, Stock_collage, Original_art, Cart_item
from artevenue.models import Product_view, Promotion, Order, Voucher, Voucher_user, Cart_item_view
from artevenue.models import Cart_user_image, Cart_stock_image, Cart_stock_collage, Cart_original_art
from artevenue.models import Order_stock_image, Order_stock_collage, Order_original_art, Order_user_image
from artevenue.models import Referral, Egift_redemption, Egift, Order_items_view, Voucher_used
from artevenue.models import Order_shipping, Order_billing, Collage_stock_image, UserProfile
from .product_views import *
from .user_image_views import *
from .tax_views import *
from .price_views import *
from .cart_views import *
import csv

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
env = settings.EXEC_ENV

## Offer 20% off to user who had logged in and created carts but didn't make any purchase.
def get_20_off_data():
	dt = datetime.datetime.strptime('2019-10-01', "%Y-%m-%d").date()
	carts = Cart.objects.filter(updated_date__date__gte = dt).exclude(
		cart_status  = 'CO').exclude(cart_status = 'AB').exclude(user_id = None)
	
	file_nm = "offer_20.csv"
	with open(file_nm, 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row =['user_id', 'username', 'first_name', 'last_name', 'email', 'phone', 'cart_id', 'cart_total']
		wr.writerow(row)
		for c in carts:	
			print(c)
			## check for user profile
			try:
				p = UserProfile.objects.get(user = c.user)
			except UserProfile.DoesNotExist:
				p = None
				
			## check if checkout was done
			if not p:
				o = Order.objects.filter(user = c.user).last()
			
			contact_number = "N/A"
			if p :
				contact_number = p.phone_number
			elif o:
				print(o)
				bill = Order_billing.objects.filter(order_id = o.order_id).first()
				if bill:
					contact_number = bill.phone_number
				else:
					ship = Order_billing.objects.filter(order_id = o.order_id).first()
					if ship:
						contact_number = ship.phone_number
			
			
			row =[c.user_id, c.user.username, c.user.first_name, c.user.last_name, 
					c.user.email, contact_number, c.cart_id, c.cart_total]
			wr.writerow(row)
	
######################################################################
## This methods removes the existing voucher from the given carts,
## and applies the the 20% off voucher
######################################################################
def apply_20_off_offer(cart_ids=None):
	
	if not cart_ids:
		return
	
	for c in cart_ids:
		try :
			cart = Cart.objects.get(cart_id = c)
		except Cart.DoesNotExist:
			cart = None
			print("Cart Id: " + cart_id + " not found")
			continue
			
		if cart:
			request = HttpRequest()
			request.user = cart.user.username
			
			if not request.user:
				print("User for cart id " + cart.cart_id + " not found")
				continue
				
			# Remove existing voucher
			res = remove_voucher(request, cart.cart_id)
			rep = json.loads(res.content.decode('utf-8'))
			if rep['status'] == 'FAILURE':
				print("Error occured while removing existing voucher " + cart.cart_id + " not found")
				continue
			else:
				print(rep)
				
			## Apply 20% off voucher "U2slzt"
			vou = apply_voucher_py_new(request, cart.cart_id, 'U2slzt', 0, 0)
			rep_v = json.loads(vou.content.decode('utf-8'))
			if rep_v['status'] == 'FAILURE':
				print("Error occured while applying this voucher " + cart.cart_id + " not found")
				continue
			else:
				print(rep_v)
	
		print("Done for " + str(c) )
		print("=================================================")
	
	print ("Finished.")
	return

def remove_offer_vocher(cart_id):
	try :
		cart = Cart.objects.get(cart_id = cart_id)
	except Cart.DoesNotExist:
		cart = None
		print("Cart Id: " + cart_id + " not found")
		return

	request = HttpRequest()
	request.user = cart.user.username
	if not request.user:
		print("User for cart id " + cart.cart_id + " not found")
		return
		
	# Remove existing voucher
	res = remove_voucher(request, cart.cart_id)
	rep = json.loads(res.content.decode('utf-8'))
	if rep['status'] == 'FAILURE':
		print("Error occured while removing existing voucher " + cart.cart_id + " not found")
	else:
		print(rep)

def offer_20_01oct2020():
	ids = [1442, 1454, 1460, 1470, 1504, 1510]
	apply_20_off_offer(ids)
	
	

######################################################################
## This methods removes the existing voucher from the given carts,
## and applies the the 25% off voucher
######################################################################
def apply_25_off_offer(cart_ids=None):
	
	if not cart_ids:
		return
	
	for c in cart_ids:
		try :
			cart = Cart.objects.get(cart_id = c)
		except Cart.DoesNotExist:
			cart = None
			print("Cart Id: " + cart_id + " not found")
			continue
			
		if cart:
			request = HttpRequest()
			request.user = cart.user.username
			
			if not request.user:
				print("User for cart id " + cart.cart_id + " not found")
				continue
				
			# Remove existing voucher
			res = remove_voucher(request, cart.cart_id)
			rep = json.loads(res.content.decode('utf-8'))
			if rep['status'] == 'FAILURE':
				print("Error occured while removing existing voucher " + cart.cart_id + " not found")
				continue
			else:
				print(rep)
				
			## Apply 25% off voucher "ZR6oB8"
			vou = apply_voucher_py_new(request, cart.cart_id, 'ZR6oB8', 0, 0)
			rep_v = json.loads(vou.content.decode('utf-8'))
			if rep_v['status'] == 'FAILURE':
				print("Error occured while applying this voucher " + cart.cart_id + " not found")
				continue
			else:
				print(rep_v)
	
		print("Done for " + str(c) )
		print("=================================================")
	
	print ("Finished.")
	return
	
def apply_voucher_py(request, cart_id, voucher_code, cart_total):
	status = "SUCCESS"	
	if voucher_code == '':
		return JsonResponse({"status":"INVALID-CODE"})
	try: 
		user = User.objects.get(username = request.user)
	except User.DoesNotExist:
		user = None	
		
	voucher = Voucher.objects.filter(voucher_code = voucher_code, effective_from__lte = today, 
			effective_to__gte = today, store_id = settings.STORE_ID).first()			
	if not voucher :
		return JsonResponse({"status":"INVALID-CODE"})

	############################################
	## Get eGift record for logged in user
	############################################	
	if user is not None:
		try:
			eGift = Egift.objects.get(voucher = voucher, receiver = user)		
		except Egift.DoesNotExist:
			eGift = {}
	else:
		eGift = {}	
	############################################
	## END: Get eGift record for logged in user
	############################################	


	############################################
	## Get the active cart and any voucher disc 
	## already applied
	############################################	
	cart = Cart.objects.filter(cart_id = cart_id, cart_status = "AC").first()	
	# Check if voucher discount is already applied to cart
	if cart.voucher_disc_amount:
		applied_disc = cart.voucher_disc_amount
	else:
		applied_disc = 0
	############################################
	## END:  Get the active cart and any voucher disc 
	## already applied
	############################################	
	

	#############################################
	## Check if voucher applies to the user, 
	## if it's already used and the expiry date
	############################################	
	voucher_user = Voucher_user.objects.filter(voucher = voucher, effective_from__lte = today, 
			effective_to__gte = today).first()	
	if not voucher.all_applicability:
		if not voucher_user :
			return JsonResponse({"status":"INVALID-CODE"})

		if voucher_user.used_date != None :
			return JsonResponse({"status":"USED"})		
		
		if voucher_user.user != user:
			return JsonResponse({"status":"USER-MISMATCH"})
	
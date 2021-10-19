from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

from artevenue.models import Ecom_site, Voucher, Voucher_user, Egift
from artevenue.views import staff_views

ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
env = settings.EXEC_ENV

def spin_wheel(request):

	return render(request, "spinwheel/spin_wheel.html")
	
@csrf_exempt
@login_required	
def set_prize(request):
	today = datetime.date.today()	
	status = 'APPLIED'
	msg = 'OK'
	voucher_code = "TESTING"

	user_id = request.POST.get('user_id','')
	prize = request.POST.get('prize','').replace("%","")
	
	if request.user.is_authenticated:
		try:			
			user = User.objects.get(username = request.user)
			user_id = user.id
			email_id = user.email
		except User.DoesNotExist:
			user = None
	else:
		user = None
	
	## Check if any active system created voucher exists for this user
	sys_voucher = Voucher_user.objects.filter(user = user, effective_to__gte = today, used_date__isnull = True).first()
	if sys_voucher:
		err_flag = True
		msg = 'Untilized or partially utilized coupon exists for you. Please use this coupon first.'
		voucher_code = sys_voucher.voucher.voucher_code
		voucher_amt = 0
		voucher_bal = 0
		voucher_expiry = sys_voucher.effective_to
	else:
		if prize.upper() == 'FREE':
			## Create CASH voucher
			None
		else:
			eff_fm = today
			eff_to = datetime.datetime.now() + relativedelta(months=3)
			## Create DISCOUNT voucher
			perc = float(prize)		
			res = staff_views.create_user_voucher(user_id, email_id, perc, eff_fm, eff_to)
			if 'err_flag' in res:
				eff_flag = res['err_flag']
				err_msg = res['err_msg']
			else:
				err_flag = False
				err_msg = ''
			if err_flag :
				msg = err_msg
			elif 'voucher_code' in vou:
				voucher_code = res['voucher_code']
	
	if err_flag:
		status = 'NOT-APPLIED'
	
	return( JsonResponse({'status': status, 'msg':msg, 'voucher_code':voucher_code}, safe=False) )
	
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count
from django.forms import modelformset_factory
from django.contrib.admin.views.decorators import staff_member_required
from artevenue.decorators import is_chief

from datetime import datetime
import datetime
import json

from django.contrib.auth.models import User

from artevenue.models import Ecom_site, Business_profile, Profile_group, Profile_group
from artevenue.views import email_sms_views

today = datetime.date.today()

def profile_group(request):

	return render(request, "artevenue/architect_registration.html", {})
	
@is_chief
def pending_business_accounts(request):

	pending_accounts = Business_profile.objects.filter(profile_group__isnull = True,
			approval_date__isnull = True)
			
	profiles = Profile_group.objects.filter(effective_from__lte = today,
		effective_to__gte = today)
	
	return render(request, "artevenue/pending_business_accounts.html", {
			'pending_accounts':pending_accounts, 'profiles':profiles})
	
@staff_member_required	
def business_account_approval(request):

	id = request.POST.get('id', '')
	user_id = request.POST.get('user_id', '')
	profile_group = request.POST.getlist('profile_group', [])
	appr_date = request.POST.get('approval_date', '')

	accnt = {}
	business_accnt = {}
	user = {}
	if appr_date != '':
		approval_date = datetime.datetime.strptime( appr_date, '%Y-%m-%d' )
	else:
		approval_date = None
		
	if	user_id :
		try:
			user = User.objects.get(pk = user_id)
		except User.DoesNotExist:
			None
		
	if id != '' and profile_group != '':
		try:
			business_accnt = Business_profile.objects.get(id = id, profile_group__isnull = True, user = user,
				approval_date__isnull = True)
		except Business_profile.DoesNotExist:
			None
			
	# Update profile group and approval date
	if business_accnt:
		accnt = Business_profile(
			id = id,
			user = business_accnt.user,
			contact_name = business_accnt.contact_name,
			company =  business_accnt.company,
			profile_group_id = profile_group[0],
			address_1 = business_accnt.address_1,
			address_2 = business_accnt.address_2,
			city = business_accnt.city,
			state = business_accnt.state,
			pin_code = business_accnt.pin_code,
			country = business_accnt.country,
			phone_number = business_accnt.phone_number,
			# email_id  = models.EmailField(blank=True, default='')  -- Same as 'User' email
			gst_number = business_accnt.gst_number,
			tax_id = business_accnt.tax_id,
			approval_date = approval_date,
			created_date = business_accnt.created_date,
			updated_date = today
		)
		accnt.save()
		
		## send email
		email_sms_views.send_business_account_approval_email(request, id)
		
	return render(request, "artevenue/business_account_approval.html", {'accnt':accnt})
	

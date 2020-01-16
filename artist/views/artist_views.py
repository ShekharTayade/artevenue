from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from artist.models import Artist_group, Artist_sms_email, Artist, Artist_original_art
from artevenue.models import Country, State, City, Pin_code, Ecom_site, Original_art

from artist.forms import artistGroupForm, artistRegisterForm, artistUserForm, artistProfileForm
from artevenue.forms import registerForm


from django.contrib import messages
import datetime

ecom = Ecom_site.objects.get(pk=settings.STORE_ID)

def register_as_artist(request, email=None):
	msg =''
	if request.method == 'POST':	
		next = request.POST['curr_pg']
		form = artistUserForm(request.POST)
		artistform = artistRegisterForm(request.POST)
		if form.is_valid():
			if artistform.is_valid():
				user = form.save()
				auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				
				artistf = artistform.save(commit=False)
				artistf.user = user
				artistf.save()

				# Update email, sms table				
				tday = datetime.datetime.today()
				a_email = Artist_sms_email(
					user = user,
					msg_type = 'NEW-ACCNT',
					email_sent = False,
					sms_sent = False,
					created_date = tday,	
					updated_date = tday
				)
				a_email.save()
				
				# After successful sign up redirect to cuurent page
				return redirect('artist_registration_confirmation', id=user.id)
	else:
		email = request.GET.get('email', '')
		if email:
			form = artistUserForm({'email':email})
			artistform = artistRegisterForm()
		else:
			form = artistUserForm()
			artistform = artistRegisterForm()


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
		
		
	return render(request, "artist/artist_registration.html", {'form':form, 
			'artistform':artistform, 'country_arr':country_arr, 'state_arr':state_arr,
			'city_arr':city_arr, 'pin_code_arr':pin_code_arr} )
	
@login_required
def artist_registration_confirmation(request, id):

	try:
		artist = Artist.objects.get(user_id=id)
	except Artist.DoesNotExist:
		artist = {}
	return render(request, "artist/artist_registration_confirmation.html", {'artist':artist} )


@login_required
def create_artist_profile(request, id):

	try:
		artist = Artist.objects.get(user_id=id)
	except Artist.DoesNotExist:
		artist = {}
	return render(request, "artist/create_artist_profile.html", {'artist':artist} )

@login_required
def artist_webpage(request, profile_name, cat_id = '', page = 1):
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '50')

	if page is None or page == 0:
		page = 1 # default

	try:

		#name = profile_name.replace("_", " ")
		artist = Artist.objects.get(url_name__icontains=profile_name)
		form = artistProfileForm(instance=artist)
	except Artist.DoesNotExist:
		artist = {}

	a_prods = Artist_original_art.objects.filter(artist_id = artist.artist_id).values('product_id')
	products = Original_art.objects.filter(product_id__in = a_prods, 
				is_published = True)
				
	if show == None :
		show = 50
	
	if show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
			show = '100'
		else:
			if show == '1000':
				perpage = 1000
				show = '1000'
			else:
				show = '50' # default
				perpage = 50
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')
	
	prods = paginator.get_page(page)			
	
	#=====================
	index = prods.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
				
	return render(request, "artist/artist_webpage.html", {'form':form,
		'artist':artist,'prods':prods} )


@staff_member_required
def create_artist_group(request):
	##curr_groups = Artist_group.objects.all()
	if request.method == 'POST':	
		next = request.POST['curr_pg']
		form = registerForm(request.POST)

		if form.is_valid():
			grp = form.save()

			# After successful sign up redirect to current page
			return redirect('index')
	else:
		form = artistGroupForm()
		
	return render(request, "artist/create_artist_group.html", {'form':form,
			##'curr_groups':curr_groups
			})
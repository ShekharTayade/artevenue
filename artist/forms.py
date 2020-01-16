from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth.models import User

from tinymce.widgets import TinyMCE

from artist.models import Artist_group, Artist
from artevenue.models import Ecom_site, Publisher

from artevenue.validators import validate_image_size, validate_india_mobile_no

ecom = Ecom_site.objects.get(pk=settings.STORE_ID )

class artistGroupForm(forms.ModelForm):
	class Meta:
		model = Artist_group
		fields = ('group_id','name', 'original_referral_fee_type', 'original_art_referral_fee',
				 'art_print_referral_fee_type', 'art_print_referral_fee')


class artistUserForm(UserCreationForm):
	email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
	class Meta:
		model = User
		fields = ('username','first_name', 'last_name', 'email', 'password1', 
				 'password2')

class artistRegisterForm(forms.ModelForm):
	store = forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	)
	artist_group = forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	)
	artist_profile = forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	)
	publisher = forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	)
	gallary_url = forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	)
	default_original_art_price= forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	)
	address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Suit / Floor / Building'}),
		required=True
	) 
	address_2 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Street / Locality'}),
		required=False
	) 
	pin_code = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	city = forms.CharField(
		widget=forms.TextInput(),
		required=True
	)		
	phone_number= forms.CharField( widget=forms.TextInput(
		attrs={'placeholder': 'Enter your 10 digit mobile number without prefix +91, or 0.'}
		),
		required=True,
		validators=[validate_india_mobile_no]
	)
	alternate_phone_number= forms.CharField( widget=forms.TextInput(
		attrs={'placeholder': 'Enter your 10 digit mobile number without prefix +91, or 0.'}
		),
		required=False,
		validators=[validate_india_mobile_no]
	)
	
	def clean_artist_group(self):
		try:
			grp= Artist_group.objects.get(pk = 'GEN')
		except grp.DoesNotExist:
			grp = None
		return grp
		
	def clean_artist_profile(self):
		return ''

	def clean_publisher(self):
		try:
			pub= Publisher.objects.get(pk = '01')
		except Publisher.DoesNotExist:
			pub = None
		return pub
		
	def clean_gallary_url(self):
		return ''

	def clean_default_original_art_price(self):
		return None
	
	def clean_store(self):
		return ecom

	class Meta:
		model = Artist
		fields = ('address1', 'address2', 'city', 'state', 'pin_code','country', 'store',
		'phone_number', 'alternate_phone_number',
		'artist_group', 'artist_profile', 'publisher', 'gallary_url',
		'default_original_art_price')
				

class artistProfileForm(forms.ModelForm):
	artist_profile = forms.CharField(widget=TinyMCE(attrs={'cols': 100, 'rows': 12}),
						#widget=forms.TextInput(attrs={'readonly':'readonly'})
						)
	
	class Meta:
		model = Artist
		fields = ('artist_profile', 'gallary_url')

	

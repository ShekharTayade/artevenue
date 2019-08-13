from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from artevenue.models import Business_profile, Contact_us, User_image, Pin_code, Referral
from artevenue.models import User_shipping_address, User_billing_address, Profile_group, Egift
from artevenue.validators import validate_artevenue_email, validate_contact_name
from artevenue.validators import validate_image_size, validate_india_mobile_no
from django.core.validators import validate_slug, MinLengthValidator

from django.shortcuts import get_object_or_404

from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from string import Template
from django.forms import ImageField
import datetime
from django.conf import settings
from artevenue.models import Ecom_site

class registerForm(UserCreationForm):
	email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 
				 'password2')
	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username__iexact=username).exists():
			raise ValidationError("This username already taken")
		return username
		
class businessuserForm(UserCreationForm):
	email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
	class Meta:
		model = User
		fields = ('username','email', 'password1', 
				 'password2')

        
class businessprofile_Form(forms.ModelForm):
	address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Suit / Floor / Building'}),
		required=False
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
		required=False
	)	
	
	phone_number= forms.CharField( widget=forms.TextInput(
		attrs={'placeholder': 'Enter your 10 digit mobile number without prefix +91, or 0.'}
		),
		required=False,
		validators=[validate_india_mobile_no]
	)	
	
	def clean_pin_code(self):
		pc = self.cleaned_data['pin_code']

		try:
			pincodeObj = Pin_code.objects.get(pk = pc)
		except Pin_code.DoesNotExist:
			pincodeObj = None

		return pincodeObj
    
	class Meta:
		model = Business_profile
		fields = ('contact_name', 'phone_number', 'company', 'address_1', 'address_2',
			'city', 'state', 'pin_code', 'country','gst_number',
			'bank_name', 'bank_branch', 'bank_acc_no', 'ifsc_code')

class pendingbusinessprofile_Form(forms.ModelForm):
	class Meta:
		model = Business_profile
		fields = '__all__'			
        
class contactUsForm(forms.ModelForm):
	phone_number= forms.CharField( widget=forms.TextInput(
		attrs={'placeholder': 'Enter your 10 digit mobile number without prefix +91, or 0.'}
		),
		required=False,
		validators=[validate_india_mobile_no]
	)
    
	class Meta:
		model = Contact_us
		fields = '__all__'
        
class User_imageForm(forms.ModelForm):
	image_to_frame = forms.ImageField(
		validators=[validate_image_size],
		required=True
	)	
	class Meta:
		model = User_image
		fields = '__all__'

        
class businessprof_Form(forms.ModelForm):
	address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Suit / Floor / Building'}),
		required=False
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
		required=False
	)	
	
	phone_number= forms.CharField( widget=forms.TextInput(
		attrs={'placeholder': 'Enter your 10 digit mobile number without prefix +91, or 0.'}
		),
		required=False,
		validators=[validate_india_mobile_no]
	)

	#profile_group = forms.CharField( widget=forms.HiddenInput() )		
	#id = forms.CharField( widget=forms.HiddenInput() )		
	
	def clean_pin_code(self):
		pc = self.cleaned_data['pin_code']

		try:
			pincodeObj = Pin_code.objects.get(pk = pc)
		except Pin_code.DoesNotExist:
			pincodeObj = None

		return pincodeObj

	#def clean_profile_group(self):
	#	profile_cd = self.cleaned_data['profile_group']

	#	try:
	#		profileObj = Profile_group.objects.get(pk = profile_cd)
	#	except Profile_group.DoesNotExist:
	#		profileObj = None
	#	return profileObj		
		
	class Meta:
		model = Business_profile
		fields = ('id', 'contact_name', 'phone_number', 'company', 
			'address_1', 'address_2',
			'city', 'state', 'pin_code', 'country','gst_number',
			'bank_acc_no', 'ifsc_code', 'bank_name', 'bank_branch')		
		
		
class userForm(forms.ModelForm):
	id = forms.CharField(
		widget=forms.HiddenInput(),
		required=True,
		#disabled=True
	) 	
	username = forms.CharField(
		widget=forms.TextInput(attrs={'readonly':'readonly'}),
		required=True,
		#disabled=True
	) 	
	email = forms.CharField(max_length=254, 
		required=True, 
		widget=forms.EmailInput(attrs={'readonly':'readonly'}),
		#disabled=True
		)	
	last_login = forms.DateTimeField( 
		required=True, 
		widget=forms.DateTimeInput(attrs={'readonly':'readonly'}),
		#disabled=True
		)	

	class Meta:
		model = User
		fields = ('id', 'username', 'first_name', 'last_name',
			'email', 'last_login')
			
class shipping_addressForm(forms.ModelForm):
	store = forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	) 
	user = forms.CharField(
		widget=forms.HiddenInput(),
	) 
	address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Flat / House No./ Floor / Building'}),
		required=False
	) 
	address_2 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Colony / Street / Locality'}),
		required=False
	) 
	pin_code = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)
	def clean_pin_code(self):
		pc = self.cleaned_data['pin_code']
		try:
			pincodeObj = Pin_code.objects.get(pk = pc)
		except Pin_code.DoesNotExist:
			pincodeObj = None

		return pincodeObj

	def clean_store(self):

		try:
			storeObj = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
		except Ecom_site.DoesNotExist:
			storeObj = None

		return storeObj
		
	def clean_user(self):
		u = self.cleaned_data['user']
		try:
			userObj = User.objects.get(pk = u)
		except User.DoesNotExist:
			userObj = None

		return userObj

	class Meta:
		model = User_shipping_address
		fields = ('store', 'full_name', 'company', 'address_1', 'address_2',
		'land_mark', 'city', 'state', 'pin_code', 'country',
		'phone_number', 'email_id', 'pref_addr', 'user')

		
class billing_addressForm(forms.ModelForm): 
	store = forms.CharField(
		widget=forms.HiddenInput(),
		required=False
	) 
	user = forms.CharField(
		widget=forms.HiddenInput(),
	) 
	address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Flat / House No./ Floor / Building'}),
		required=False
	) 
	address_2 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Colony / Street / Locality'}),
		required=False
	) 
	pin_code = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)
	
	def clean_pin_code(self):
		pc = self.cleaned_data['pin_code']

		try:
			pincodeObj = Pin_code.objects.get(pk = pc)
		except Pin_code.DoesNotExist:
			pincodeObj = None

		return pincodeObj

	def clean_store(self):
		try:
			storeObj = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
		except Ecom_site.DoesNotExist:
			storeObj = None

		return storeObj

	def clean_user(self):
		u = self.cleaned_data['user']
		try:
			userObj = User.objects.get(pk = u)
		except User.DoesNotExist:
			userObj = None

		return userObj

	class Meta:
		model = User_billing_address
		fields = ('store', 'full_name', 'company', 'address_1', 'address_2',
		'land_mark', 'city', 'state', 'pin_code', 'country',
		'phone_number', 'email_id', 'gst_number', 'pref_addr', 'user')

class referralForm(forms.ModelForm):
	email_id = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
	class Meta:
		model = Referral
		exclude = ('referred_by', 'referred_date', 'referred_by_claimed_date',
			'referee_claimed_date')
			
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(referralForm, self).__init__(*args, **kwargs)
		
	def clean_email_id(self):
		email_id = self.cleaned_data['email_id']
		if self.user.email == email_id :
			raise ValidationError("You can't refer yourself :-)")
		return email_id


class egiftForm(forms.ModelForm):
	receiver_email = forms.CharField(max_length=254, required=True, 
			label='Email ID of the person you are sending the gift card to:',
			help_text = 'Please enter Email Id of the receiver',
			widget=forms.EmailInput()
		)
	receiver_name = forms.CharField(max_length=600, required=True,
			label='Who do you want to send the gift card to:',
			strip=True,
			help_text = 'Please enter name of the receiver',
			widget=forms.TextInput()
		)
	receiver_phone = forms.CharField(max_length=600, required=True,
			label='Mobile Number of the receiver:',
			strip=True,
			validators=[validate_india_mobile_no],
			widget=forms.TextInput()
		)
	delivery_date = forms.DateField(input_formats = ['%Y-%m-%d','%m/%d/%Y','%m/%d/%y'],
			initial=datetime.date.today(),
			label='When would you like us to deliver the gift card:',
			help_text="If left blank, we will send it immediately",
			widget=forms.DateInput(),
			required=True
		)
	gift_amount = forms.DecimalField(
			min_value=500, max_value=100000, decimal_places=2,
			label='Let us know the value of gift card you want to send:',
			help_text="Min: Rs. 500, Max: Rs. 1,00,000",
			widget=forms.NumberInput({'step': '100'}),
			required=True
		)
		
	message = forms.CharField(max_length=2000, required=True,
			label='Write your message:',
			strip=True,
			help_text='We will include this message in the email we send (Max 2000 chars)',
			widget=forms.Textarea(attrs={'rows':4, 'cols':15})
		)
		
	gift_date = forms.DateField(
		widget=forms.HiddenInput(),
		required = False,
		initial=datetime.date.today()
	)		
	class Meta:
		model = Egift
		exclude = ('giver', 'receiver', 'voucher', 'payment_status',
					'giver_email_sent', 'receiver_email_sent', 'card_image' )
			
	def __init__(self, *args, **kwargs):
		self.giver = kwargs.pop('giver', None)
		super(egiftForm, self).__init__(*args, **kwargs)
		
	def clean_email_id(self):
		email_id = self.cleaned_data['receiver_email']
		if self.user.email == email_id :
			raise ValidationError("Please don't gift yourself :-)")
		return email_id
		
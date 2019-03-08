from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from artevenue.models import Business_profile, Contact_us, User_image, Pin_code
from artevenue.models import User_shipping_address, User_billing_address, Profile_group
from artevenue.validators import validate_artevenue_email, validate_contact_name
from artevenue.validators import validate_image_size, validate_india_mobile_no

from django.core.validators import validate_slug, MinLengthValidator

from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from django.utils.translation import gettext_lazy as _

from string import Template
from django.forms import ImageField


class registerForm(UserCreationForm):
	email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 
				 'password2')

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
			'city', 'state', 'pin_code', 'country','gst_number')

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
		fields = ('id', 'contact_name', 'phone_number', 'company', 'address_1', 'address_2',
			'city', 'state', 'pin_code', 'country','gst_number')		
		
		
class userForm(forms.ModelForm):
	username = forms.CharField(
		widget=forms.TextInput(),
		required=True,
		disabled=True
	) 	
	email = forms.CharField(max_length=254, 
		required=True, 
		widget=forms.EmailInput(),
		disabled=True)	
	last_login = forms.DateTimeField( 
		required=True, 
		widget=forms.DateTimeInput(),
		disabled=True)	

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name',
			'email', 'last_login')
			
class shipping_addressForm(forms.ModelForm):
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

	class Meta:
		model = User_shipping_address
		fields = ('full_name', 'company', 'address_1', 'address_2',
		'land_mark', 'city', 'state', 'pin_code', 'country',
		'phone_number', 'email_id', 'pref_addr')

		
class billing_addressForm(forms.ModelForm):
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

	class Meta:
		model = User_billing_address
		fields = ('full_name', 'company', 'address_1', 'address_2',
		'land_mark', 'city', 'state', 'pin_code', 'country',
		'phone_number', 'email_id', 'pref_addr')
	
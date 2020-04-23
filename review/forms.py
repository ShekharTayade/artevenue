from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from artevenue.models import Pin_code, Referral, Order, UserProfile, Channel_partner
from artevenue.validators import validate_artevenue_email, validate_contact_name
from artevenue.validators import validate_image_size, validate_india_mobile_no

from django.shortcuts import get_object_or_404

from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from django.core.exceptions import ValidationError

from string import Template
from django.forms import ImageField
import datetime
from django.conf import settings
from artevenue.models import Ecom_site
from review.models import Customer_review_stock_image

class CustomerReviewForm(forms.ModelForm):
	review_id = forms.IntegerField( widget=forms.HiddenInput() )
	email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
	phone_number= forms.CharField( widget=forms.TextInput(
		attrs={'placeholder': 'Enter your 10 digit mobile number without prefix +91, or 0.'}
		),
		required=False,
		validators=[validate_india_mobile_no]
	)	
	comments = forms.CharField(max_length=2000, required=True, 
		widget=forms.Textarea(attrs={'placeholder': 'What you liked/disliked'})
	)
	headline = forms.CharField(max_length=100, required=True, 
		widget=forms.Textarea(attrs={'placeholder': 'A brief title/head of your review'})
	)
	posted_date = forms.DateField( widget=forms.HiddenInput() )
	order_id = forms.IntegerField( widget=forms.HiddenInput() )
	
	class Meta:
		model = Customer_review_stock_image
		fields = ('review_id', 'user', 'name', 'email_id', 'phone_number', 
		'location', 'country', 'product', 'rating', 'headline', 'comments', 
		'order_id')		
		

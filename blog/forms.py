from django import forms
from django.contrib.auth.models import User

import datetime
from django.conf import settings
from artevenue.models import Ecom_site
from blog.models import Blog_post, Blog_author

class BlogPostForm(forms.ModelForm):
	class Meta:
		model = Blog_post
		fields = ('author', 'title', 'post', 'is_published', 'date_published')

class BlogAuthorForm(forms.ModelForm):
	class Meta:
		model = Blog_author
		fields = ('website_url', 'instagram_url', 'twitter_url', 'profile', 'profile_pic')


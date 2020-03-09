from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from tinymce.models import HTMLField

class Blog_author(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
	website_url = models.SlugField(max_length = 500, null= True, blank = True)
	facebook_url = models.SlugField(max_length = 500, null= True, blank = True)
	instagram_url = models.SlugField(max_length = 500, null= True, blank = True)
	twitter_url = models.SlugField(max_length = 500, null= True, blank = True)
	profile = models.CharField(max_length = 2000, blank=False, null = False)
	profile_pic = models.ImageField(upload_to='egift_cards/%Y/%m/%d/', blank=True, default="")
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)		
	
	
class Blog_post(models.Model):
	post_id = models.AutoField(primary_key=True, null=False)
	author = models.ForeignKey(Blog_author, models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length = 600, blank=False, null = False)
	post = HTMLField()
	is_published = models.BooleanField(null=False, default=False)
	date_published = models.DateTimeField(null=False, default=False)
	expiry_date = models.DateTimeField(null=True)
	background_image_url = models.SlugField(max_length = 500, null= True, blank = True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)		

	def __str__(self):
		return self.title
	
class Blog_post_comment(models.Model):
	comment_id = models.AutoField(primary_key=True, null=False)
	blog_post = models.ForeignKey(Blog_post, on_delete=models.CASCADE, null=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	comment = models.CharField(max_length = 2000, blank=False, null = False)
	is_published = models.BooleanField(null=False, default=False)
	date_published = models.DateTimeField(null=False, default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)		

	def __str__(self):
		return str(self.comment_id)

class Blog_post_comment_reply(models.Model):
	reply_id = models.AutoField(primary_key=True, null=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	blog_post = models.ForeignKey(Blog_post, on_delete=models.CASCADE, null=False)
	blog_post_comment = models.ForeignKey(Blog_post_comment, on_delete=models.CASCADE, null=False)
	reply = models.CharField(max_length = 2000, blank=False, null = False)
	is_published = models.BooleanField(null=False, default=False)
	date_published = models.DateTimeField(null=False, default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=False)
	updated_date = models.DateTimeField(auto_now=True, null=False)

	def __str__(self):
		return str(self.reply_id)

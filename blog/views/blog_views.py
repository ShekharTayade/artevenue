from django.shortcuts import render, redirect
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


from datetime import datetime
import datetime


from artevenue.models import Ecom_site 
from blog.models import Blog_author, Blog_post, Blog_post_comment, Blog_post_comment_reply

from blog.forms import BlogPostForm

today = datetime.date.today()


def blog(request):

	blogs = Blog_post.objects.order_by('-date_published')
		
	return render(request, "blog/blog_list.html", {'blogs':blogs})
	

def get_blog(request, post_id):
	try:
		blog = Blog_post.objects.get(post_id = post_id)
		blog_post_comment = Blog_post_comment.objects.filter(blog_post = blog).order_by('-updated_date')
		blog_post_comment_ids = blog_post_comment.values_list('comment_id', flat=True)
		blog_post_comment_reply = Blog_post_comment_reply.objects.filter(blog_post_comment__in = blog_post_comment_ids).order_by('-updated_date')
	except Blog_post.DoesNotExist:
		blog = {}

	return render(request, "blog/blog_post.html", {'blog':blog,
			'blog_post_comment':blog_post_comment, 'blog_post_comment_reply':blog_post_comment_reply})

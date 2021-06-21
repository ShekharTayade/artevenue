from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from artevenue.models import Employee, Business_profile
from artist.models import Artist

def is_manager(function):
	def wrap(request, *args, **kwargs):
		try:
			userObj = User.objects.get(username = request.user)
		except User.DoesNotExist:
			userObj = None
		if userObj:
			try:
				if userObj.employee.is_manager:
					return function(request, *args, **kwargs)
				else:
					raise PermissionDenied
			except Employee.DoesNotExist:
					raise PermissionDenied
		else:
			raise PermissionDenied
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap
	
def is_chief(function):
	def wrap(request, *args, **kwargs):
		try:
			userObj = User.objects.get(username = request.user)
		except User.DoesNotExist:
			userObj = None
		if userObj:
			try:
				if userObj.employee.is_chief:
					return function(request, *args, **kwargs)
				else:
					raise PermissionDenied
			except Employee.DoesNotExist:
					raise PermissionDenied
		else:
			raise PermissionDenied
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap
	
	
def is_artist(function):
	def wrap(request, *args, **kwargs):
		try:
			userObj = User.objects.get(username = request.user)
		except User.DoesNotExist:
			userObj = None
		if userObj:
			try:
				artist = Artist.objects.get(user = userObj)
				if artist:
					return function(request, *args, **kwargs)
				else:
					raise PermissionDenied
			except Artist.DoesNotExist:
					raise PermissionDenied
		else:
			raise PermissionDenied
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap



def is_livspace_admin(function):
	def wrap(request, *args, **kwargs):
		try:
			userObj = User.objects.get(username = request.user)
		except User.DoesNotExist:
			userObj = None
		if userObj:			
			try:
				bp = Business_profile.objects.get( user=userObj)
				if bp.business_code == 'LIV1':
					return function(request, *args, **kwargs)
				else:
					raise PermissionDenied
			except Business_profile.DoesNotExist:
					raise PermissionDenied
		else:
			raise PermissionDenied
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap


def is_artist(function):
	def wrap(request, *args, **kwargs):
		try:
			userObj = User.objects.get(username = request.user)
			artist = Artist.objects.get(user = userObj)
		except Artist.DoesNotExist:
			artist = None
		except User.DoesNotExist:
			userObj = None
		if userObj:
			if artist:
				return function(request, *args, **kwargs)
			else:
				raise PermissionDenied
		else:
			raise PermissionDenied

	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap
	
	
def has_accounts_access(function):
	def wrap(request, *args, **kwargs):
		try:
			userObj = User.objects.get(username = request.user)
		except User.DoesNotExist:
			userObj = None
		if userObj:
			try:
				if userObj.employee.department == 5 or userObj.employee.is_manager:
					return function(request, *args, **kwargs)
				else:
					raise PermissionDenied
			except Employee.DoesNotExist:
					raise PermissionDenied
		else:
			raise PermissionDenied
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap
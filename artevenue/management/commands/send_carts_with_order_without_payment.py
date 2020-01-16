from django.core.management.base import BaseCommand, CommandError
from artevenue.views.email_sms_views import send_carts_with_order_without_payment


class Command(BaseCommand):

	help = "Send Carts with checkout, no payment."

	def handle(self, *args, **options):
		err_flag = False
		try:
			send_carts_with_order_without_payment()
		except Exception as e:
			print (type(e)) 
			print (e) 
			err_flag = True
		
		if err_flag:
			self.stderr.write(self.style.SUCCESS('Error occured while sending cart emails.'))
		else :
			self.stdout.write(self.style.SUCCESS('Cart Email Sent'))

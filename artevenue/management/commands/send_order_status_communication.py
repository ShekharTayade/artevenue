from django.core.management.base import BaseCommand, CommandError
from artevenue.views.email_sms_views import order_status_communication_email


class Command(BaseCommand):

	help = "Send Customer Review Emails."

	def handle(self, *args, **options):
		err_flag = False
		try:
			mail_cnt = order_status_communication_email()
		except Exception as e:
			print (type(e)) 
			print (e) 
			err_flag = True
		
		if err_flag:
			self.stderr.write(self.style.SUCCESS('Error occured while sending order status emails.'))
		else :
			self.stdout.write(self.style.SUCCESS('Sent ' + str(mail_cnt) + ' order status emails.'))

from django.core.management.base import BaseCommand, CommandError
from artevenue.views.email_sms_views import send_contact_us_emails


class Command(BaseCommand):

	help = "Send Contact Us Emails."

	def handle(self, *args, **options):
		err_flag = False
		try:
			mail_cnt = send_contact_us_emails()
		except Exception as e:
			print (type(e)) 
			print (e) 
			err_flag = True
		
		if err_flag:
			self.stderr.write(self.style.SUCCESS('Error occured while sending contact us emails.'))
		else :
			self.stdout.write(self.style.SUCCESS('Sent ' + str(mail_cnt) + ' contact us emails.'))

from django.core.management.base import BaseCommand, CommandError
from artevenue.views.updatePODImageData import getMissingImages


class Command(BaseCommand):

	help = "Get Missing POD Images."

	def handle(self, *args, **options):
		err_flag = False
		try:
			getMissingImages()
		except Exception as e:
			print (type(e)) 
			print (e) 
			err_flag = True
		
		if err_flag:
			self.stderr.write(self.style.SUCCESS('Error occured while importing missing POD images'))
		else :
			self.stdout.write(self.style.SUCCESS('POD Images complete.'))

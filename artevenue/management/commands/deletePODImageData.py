from django.core.management.base import BaseCommand, CommandError
from artevenue.views.updatePODImageData import deletePODImageData


class Command(BaseCommand):

	help = "Import POD Images and Data."

	def handle(self, *args, **options):
		err_flag = False
		try:
			deletePODImageData()
		except Exception as e:
			print (type(e)) 
			print (e) 
			err_flag = True
		
		if err_flag:
			self.stderr.write(self.style.SUCCESS('Error occured while deleting POD images, data.'))
		else :
			self.stdout.write(self.style.SUCCESS('POD delete complete.'))

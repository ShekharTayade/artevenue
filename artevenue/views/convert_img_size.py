def change_image_size( path, size_width):
	from PIL import Image
	import os
	
	import pdb
	pdb.set_trace()
	
	for file in os.listdir(path):
		if file.endswith(".jpg"):
			print(os.path.join(path, file))	
			img_file = os.path.join(path, file)
			img_source = Image.open(img_file)
			w = img_source.width
			h = img_source.height
			ratio = w / h
			img150 = img_source
			img75 = img_source

			## convert to 150 X 150
			img150.resize( (150, round(150/ratio)) )
			img150.save(path + '/' + file + "150")
			
			## convert to 75 X 75
			img75.resize( (75, round(75/ratio)) )
			img75.save(path + '/' + file + "75")


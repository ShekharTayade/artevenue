from PIL import Image

single_in_a_row_sizes = [1920, 1200, 768, 600]		
two_in_a_row_sizes = [960, 600, 384, 300]		

def generate_sizes(size_type, dir, img_file, file_name):
	print("Starting....")
	img_source = Image.open(dir + "/" + img_file)
	name = img_source.filename

	r = img_source.width / img_source.height
	if size_type == "singleinrow":		
		for w in single_in_a_row_sizes:
			h = round(w/r)
			img = img_source.resize( (w, h ) )			
			f_name = file_name + "_lg.jpg" if w==1920 else file_name + "_md.jpg" if w==1200 else file_name + "_sm.jpg" if w==768 else  file_name + "_xs.jpg"
			f_name = dir + "/" + f_name
			img.save(f_name)
			
	if size_type == "twoinarow":		
		for w in two_in_a_row_sizes:
			h = round(w/r)
			img = img_source.resize( (w, h ) )			
			f_name = file_name + "_lg.jpg" if w==960 else file_name + "_md.jpg" if w==600 else file_name + "_sm.jpg" if w==384 else  file_name + "_xs.jpg"
			f_name = dir + "/" + f_name
			img.save(f_name)
	print("Done....")

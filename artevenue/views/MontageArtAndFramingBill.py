from artevenue.models import Order_items_view, Moulding
import csv, datetime, calendar
from decimal import Decimal
from django.db.models import Count, Q, Max, Sum, F, Avg

def get_production_cost(yrmonth):

	today = datetime.datetime.today()
	
	if yrmonth == '':
		year = yrmonth[3:]
		mth = yrmonth[:2] 
		yrmonth = year + '-' + mth
	
	start_date = datetime.datetime.strptime(yrmonth + '-01', "%Y-%m-%d").date()	
	month_days = calendar.monthrange(start_date.year, start_date.month)[1]
	end_date = datetime.datetime.strptime(yrmonth + '-' + str(month_days), "%Y-%m-%d").date()

	order_items = Order_items_view.objects.select_related(
		'product').filter(order__order_date__gte = start_date,
		order__order_date__lte = end_date,
		quantity__gte = 1,
		product__product_type_id = F('product_type_id')).exclude(order__order_status = 'PP').exclude(order__order_status = 'CN')

	printroyalty = Decimal(1.4)
	paperinkrate = Decimal(0.29)
	paperrate = Decimal(0.20)

	printroyalty = Decimal(1.3)
	canvasrate = Decimal(0.6)
	canvasinkrate = Decimal(0.35)

	acrrate = Decimal(0.5)
	mntrate = Decimal(0.11)
	hardbrdrate = Decimal(0.08)
	pastingbrdrate = Decimal(0.16)

	stretcherrate = Decimal(2.90)

	#framerate_box = 2.17
	#framerate_simple1 = 1.42
	#framerate_simple2 = 2.5
	frame_cost = {'11': 1.40, '22': 1.40, '8': 1.40, '23': 2.4, '24': 2.4, '10': 2.1, '25': 2.1, '26': 2.1, '18': 1.40, '20':  2.1, '6': 2.1, '29':2.1, '30': 2.1}
	

	with open('Production_Cost_' + yrmonth + '.csv', 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		row = ["MONTAGE ART AND FRAMING BILL FOR MONTH - " + yrmonth ]
		wr.writerow(row)
	
		row = ["Order No", "Order_date", "Product_id", "Product Name", "product_type", "Image Width", "Image Height",
			"Print Surface", "Frame", "Mount Size", "Stretched", "Item Total", "Production Cost"]
		wr.writerow(row)
		
		for i in order_items:
			w = i.image_width
			h = i.image_height
			mntsize = i.mount_size
			print_medium = i.print_medium_id
			
			if i.moulding:
				mld_nm = i.moulding.name
			else:
				mld_nm = ''

			sqin = Decimal(i.image_width) * Decimal(i.image_height)
			sqin_surface_paper = Decimal(w+2) * Decimal(h+2)
			sqin_surface_canvas = Decimal(w+4) * Decimal(h+4)
			rnin = w + h
			
			moulding_h = 0
			moulding_w = 0
			mld_cost = 0
			if i.moulding_id:
				moulding = Moulding.objects.filter(moulding_id = i.moulding_id).first()
				if moulding:
					if i.print_medium_id == 'PAPER':
						if i.mount_size:							
							moulding_w = w + i.mount_size*2 + moulding.width_inner_inches*2
							moulding_h = h + i.mount_size*2 + moulding.width_inner_inches*2
						else:
							moulding_w = w + moulding.width_inner_inches*2
							moulding_h = h + moulding.width_inner_inches*2
					else:
						moulding_w = w + moulding.width_inner_inches*2
						moulding_h = h + moulding.width_inner_inches*2
						
					mldrate = Decimal(frame_cost[i.moulding_id])
					mld_cost = moulding_w * mldrate + moulding_h * mldrate
			else:
				moulding = None
				
			mnt_cost = 0
			print_cost = 0 
			total_cost = 0
			acr_cost = 0
			brd_cost = 0
			str_cost = 0
			if print_medium == 'PAPER':
				if i.product_type_id == 'STOCK-IMAGE' or i.product_type_id == 'STOCK-COLLAGE':
					royalty = printroyalty
				else:
					royalty = 0
				print_cost = sqin * royalty + sqin * paperinkrate + sqin_surface_paper * paperrate
				
				mnt_size_w = 0
				if i.mount_size:
					mnt_size_w = i.mount_size*2 + w
					mnt_size_h = i.mount_size*2 + h
					mnt_cost = mntrate * mnt_size_w * mnt_size_h
				else:
					mnt_cost = 0
					mnt_size_w = 0
					mnt_size_h = 0
					
				if moulding:
					if i.mount_size:
						acr_cost =  mnt_size_w * mnt_size_h * acrrate
						brd_cost =  mnt_size_w * mnt_size_h * hardbrdrate + mnt_size_w * mnt_size_h * pastingbrdrate
					else:
						acr_cost =  w * h * acrrate
						brd_cost =  w * h * hardbrdrate + mnt_size_w * mnt_size_h * pastingbrdrate
						
					
			elif print_medium == 'CANVAS':
				if i.product_type_id == 'STOCK-IMAGE' or i.product_type_id == 'STOCK-COLLAGE':
					royalty = printroyalty
				else:
					royalty = 0
				print_cost = sqin * royalty + sqin * canvasinkrate + sqin_surface_canvas * canvasrate
				
				if i.stretch_id == 1:			
					if (w*h) >= 1290:
						str_cost = (w + h) * 3 * stretcherrate	
					elif (w*h) >= 850 and w*h < 1290:
						if w >= h:
							str_cost = ((w+h)*2 + w) * stretcherrate
						else:
							str_cost = ((w+h)*2 + h) * stretcherrate
					else:
						str_cost = (w + h) * 2 * stretcherrate

			total_cost = print_cost + mld_cost + mnt_cost + acr_cost + brd_cost + str_cost 
		
		
			## Hardware & packing material cost
			h_c = 0
			p_c = 0
			if sqin <= 100:
				h_c = 10
				p_c = 30
			elif sqin <= 144:
				h_c = 12
				p_c = 35
			elif sqin <= 225:
				h_c = 15
				p_c = 45
			elif sqin <= 324:
				h_c = 20
				p_c = 65
			elif sqin <= 576:
				h_c = 25
				p_c = 150
			elif sqin <= 600:
				h_c = 25
				p_c = 160
			elif sqin <= 864:
				h_c = 25
				p_c = 200
			elif sqin <= 1200:
				h_c = 30
				p_c = 400
			elif sqin <= 1600:
				h_c = 40
				p_c = 500
			else: 				## 2400
				h_c = 40
				p_c = 750
						
			if i.moulding:
				mld_nm = i.moulding.name
			else: 
				mld_nm = ''
			
			# Add hardware and packing material costs
			total_cost = total_cost + h_c + p_c

			#Add 10% for other production costs, such as utilities, labour
			total_cost = total_cost + + (i.item_total * 10/100)
			
			row = [i.order.order_number, i.order.order_date, i.product_id, 
				i.product.name, i.product_type_id, i.image_width, i.image_height,
				i.print_medium_id, mld_nm, i.mount_size, i.stretch_id, i.item_total, total_cost]
			wr.writerow(row)

			'''
			print(str(w) + " X " + str(h) + ", " + print_medium + ", " + mld_nm + ", mnt_size: " + str(i.mount_size))
			print("Price: " + str(i.item_total) + ", Cost: " + str(total_cost) )
			print( "Print: " + str(print_cost) + ", Frame: " + str(mld_cost) + ", Mount: " + str(mnt_cost) 
			 + ", Acr: " + str(acr_cost)  + ", board: " 
				+ str(brd_cost) + ", Strecher: " + str(str_cost) +  ", 10%: " + str((i.item_total * 10/100)) )
			print("=================================================")
			'''
	return 


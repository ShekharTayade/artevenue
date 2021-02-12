from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from artevenue.models import Order, Product_view, Promotion, Moulding, Print_medium, Mount
from artevenue.models import Acrylic, Stretch, Board, Product_type
from artevenue.models import Shipping_method, Shipper, Shipping_status
from artevenue.models import Stock_image, User_image, Stock_collage, Original_art

class Credit_note(models.Model):	
	CRN_REASON = (
		('UN', 'Not Specified'),
		('RT', 'Full Refund Issued for Customer Return'),
		('DM', 'Full Refund Issued for Damaged Delivery'),
		('PR', 'Partial Refund for Damaged Delivery'),
		('PC', 'Partial Refund for Customer Return'),
		('CA', 'Reduced Price Due to Changes to Artwork'),
		('RM', 'Artwork Removed from the Order'),
		('AD', 'Additional Discount Offered'),
		('CN', 'Order Cancelled'),
	)    

	crn_id = models.AutoField(primary_key=True)
	credit_note_number = models.CharField(max_length = 15, blank = True, default = '')
	credit_note_date = models.DateTimeField(null=True)
	order = models.ForeignKey(Order,on_delete=models.PROTECT, null=False)
	credit_note_amount = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	credit_note_reason = models.CharField(max_length = 2, choices=CRN_REASON, blank=True, default = '')
	remarks = models.CharField(max_length = 500, blank = True, default = '')
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class Credit_note_detail(models.Model):	
	crn_detail_id = models.AutoField(primary_key=True)
	credit_note = models.ForeignKey(Credit_note,on_delete=models.PROTECT, null=True)
	product_id = models.IntegerField(null=False)   ## To be referenced to Product_view
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False) 
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class Debit_note(models.Model):	
	DRN_REASON = (
		('UN', 'Not Specified'),
		('CA', 'Increased Price Due to Changes to Artwork'),
		('AA', 'Additional Artwork Added to the Order'),
		('AF', 'Increased Price Due to Additional Framing'),
		('OT', 'Increased Price Due to Other Changes'),
	)    

	drn_id = models.AutoField(primary_key=True)
	debit_note_number = models.CharField(max_length = 15, blank = True, default = '')
	debit_note_date = models.DateTimeField(null=True)
	order = models.ForeignKey(Order,on_delete=models.PROTECT, null=False)
	debit_note_amount = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	debit_note_reason = models.CharField(max_length = 2, choices=DRN_REASON, blank=True, default = '')
	remarks = models.CharField(max_length = 500, blank = True, default = '')
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class Debit_note_detail(models.Model):	
	drn_detail_id = models.AutoField(primary_key=True)
	debit_note = models.ForeignKey(Debit_note,on_delete=models.PROTECT, null=True)
	product_id = models.IntegerField(null=False)   ## To be referenced to Product_view
	promotion = models.ForeignKey(Promotion, models.PROTECT, null=True)
	quantity = models.IntegerField(null=False)
	item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	moulding = models.ForeignKey(Moulding,on_delete=models.PROTECT, null=True)
	moulding_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	print_medium = models.ForeignKey(Print_medium, models.PROTECT, null=False, default='PAPER')
	print_medium_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	mount = models.ForeignKey(Mount, models.PROTECT, null=True)
	mount_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	board = models.ForeignKey(Board, models.PROTECT, null=True)
	board_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	acrylic = models.ForeignKey(Acrylic, models.PROTECT, null=True)
	acrylic_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	stretch = models.ForeignKey(Stretch, models.PROTECT, null=True)
	stretch_size = models.DecimalField(max_digits=12, decimal_places=2, null=True)
	image_width = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)
	image_height = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)	
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False) 
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class Return_order(models.Model):	
	RET_REASON = (
		('UN', 'Not Specified'),
		('Q', 'Quality Issue'),
		('D', 'Damaged Delivery'),
		('S', 'Size Issue'),
		('N', "Don't Need It"),
		('L', 'Did not Like It'),
	)    
	RET_STATUS = (
		('RQ', 'Return Request Raised'),
		('IN', 'Return Request Being Processed'),
		('SH', 'Return Shipment Booked'),
		('PK', 'Return Shipment Picked Up'),
		('RC', 'Return Shipment Received by ArteVenue'),
		('QC', 'Quality Check In Process'),
		('QF', 'Quality Check Failed'),
		('QP', 'Quality Check Passed'),
		('RI', 'Refund Issued'),
	)
	ret_id = models.AutoField(primary_key=True)
	ret_number = models.CharField(max_length = 15, blank = True, default = '')
	ret_request_date = models.DateTimeField(null=True)
	ret_reason = models.CharField(max_length = 2, choices=RET_REASON, blank=True, default = '')
	order = models.ForeignKey(Order,on_delete=models.PROTECT, null=False)
	return_shipment_charges = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	other_deductions = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	total_deductions = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	refund_amount = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	refund_transaction_reference = models.CharField(max_length = 500, blank = True, default = '')
	remarks = models.CharField(max_length = 500, blank = True, default = '')
	ret_process_date = models.DateTimeField(null=True)
	ret_shipping_method = models.ForeignKey(Shipping_method, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup
	ret_shipper = models.ForeignKey(Shipper, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup	
	ret_shipping_status = models.ForeignKey(Shipping_status, models.PROTECT, null=True) #Null is allowed, in case it's a store pickup
	ret_status = models.CharField(max_length = 2, blank=True, 
		choices=RET_STATUS, default='PP') 
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)	


class Return_order_item(models.Model):	
	QC_FAIL_REASON = (
		('DM', 'Products Received in Damanged Condition'),
		('WR', 'Products Received Are Not As Per The Order')
	)
	ret_item_id = models.AutoField(primary_key=True)
	return_order = models.ForeignKey(Return_order,on_delete=models.PROTECT, null=True)
	ret_item_quantity = models.IntegerField(null=False)
	ret_item_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
	ret_item_sub_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	ret_item_disc_amt  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	ret_item_tax  = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	ret_item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)
	quality_check_date = models.DateTimeField(null=True)
	quality_check_passed = models.BooleanField(null=True, default=False)
	quality_check_failed_reason = models.CharField(max_length = 2, choices=QC_FAIL_REASON, blank = True, default = '')

class Return_order_stock_image(Return_order_item):
	stock_image = models.ForeignKey(Stock_image, models.CASCADE, null=False)

class Return_order_user_image(Return_order_item):
	user_image = models.ForeignKey(User_image, models.CASCADE, null=False)

class Return_order_stock_collage(Return_order_item):
	stock_collage = models.ForeignKey(Stock_collage, models.CASCADE, null=False)

class Return_order_original_art(Return_order_item):
	original_art = models.ForeignKey(Original_art, models.CASCADE, null=False)

class Return_order_item_view(models.Model):
	ret_item_id = models.AutoField(primary_key=True)
	return_order = models.ForeignKey(Return_order,on_delete=models.PROTECT, null=True)
	product_id = models.IntegerField(null=False)   ## To be referenced to Product_view
	product_type = models.ForeignKey(Product_type, models.PROTECT, null=False)
	ret_item_quantity = models.IntegerField(null=False)
	ret_item_total = models.DecimalField(max_digits=12, decimal_places=2,  null=False, default=0)

	class Meta:
		managed = False
		db_table = 'return_order_item_view'	

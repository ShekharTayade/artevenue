from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings

from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML, CSS


from artevenue.models import Order, Generate_number_by_month, Order_items_view, Ecom_site
import datetime 

from artevenue.models import Generate_number_by_month

today = datetime.datetime.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )

@staff_member_required
def store_invoices(request):
	return render(request, 'artevenue/store_invoices.html')	

@staff_member_required		
@csrf_exempt
def get_invoices(request, order_number=None, printpdf=''):
	startDt = ''
	endDt = ''	
	inv_startDt = ''
	inv_endDt = ''
	page = request.POST.get('page', 1)
	order_number = request.POST.get('order_num','')
	invoice_number = request.POST.get('invoice_num', '')
	
	import pdb
	pdb.set_trace()
	
	if printpdf == '':
		printpdf = request.POST.get('printpdf', 'NO')
	if not order_number:
		order_number = request.POST.get("order_number", '')

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")			
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")

	inv_from_date = request.POST.get("inv_fromdate", '')
	if inv_from_date != '' :
		inv_startDt = datetime.datetime.strptime(inv_from_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")			
	inv_to_date = request.POST.get("inv_todate", '')
	if inv_to_date != '' :
		inv_endDt = datetime.datetime.strptime(inv_to_date  + " 23:59:59", "%Y-%m-%d %H:%M:%S")
		
	order_list = Order.objects.filter().select_related('order_billing', 
		'order_shipping').exclude(invoice_number = '').order_by('-updated_date')
	
	order_items_list = {}
	if startDt:
		order_list = order_list.filter(order_date__gte = startDt)
	if endDt:
		order_list = order_list.filter(order_date__lte = endDt)
	if inv_startDt:
		order_list = order_list.filter(invoice_date__gte = inv_startDt)
	if inv_endDt:
		order_list = order_list.filter(invoice_date__lte = inv_endDt)

	if order_number:
		order_list = order_list.filter(order_number = order_number)	

	if invoice_number:
		order_list = order_list.filter(invoice_number = invoice_number)	
	
	if not inv_startDt and not inv_endDt and  not startDt and not endDt and not order_number and not invoice_number:
		return render(request, 'artevenue/orders_table.html', {'count':0, 
			'orders': {}, 'order_items_list':{}, 
			'startDt':startDt, 'endDt':endDt})
	order_items_list = Order_items_view.objects.select_related('product', 'promotion').filter(
		order__in = order_list, product__product_type_id = F('product_type_id'))
	
	count = order_list.count()
	
	paginator = Paginator(order_list, 5)
	orders = paginator.get_page(page)
	try:
		orders = paginator.page(page)
	except PageNotAnInteger:
		orders = paginator.page(1)
	except EmptyPage:
		orders = paginator.page(paginator.num_pages)
	
	if printpdf == "YES":
		html_string = render_to_string('artevenue/invoice_print.html', {'count':count, 
			'orders': order_list, 'order_items_list':order_items_list, 
			'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL,
			'ecom_site':ecom})

		html = HTML(string=html_string, base_url=request.build_absolute_uri())
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_inv_pdf.pdf',
			stylesheets=[CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') ],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_inv_pdf.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_inv_pdf.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/invoice_table.html', {'count':count, 
			'orders': orders, 'order_items_list':order_items_list, 
			'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL,
			'ecom_site':ecom})		

def get_next_invoice_number():
	num = 0
	#Get curentyear, month in format YYYYMM
	dt = datetime.datetime.now()
	mnth = dt.strftime("%Y%m")

	# Get suffix required 
	suffix = '-'
	# Get prefix required 
	prefix = 'INV-'
	
	monthyear = Generate_number_by_month.objects.filter(type='INVOICE-NUMBER', month_year = mnth).first()
	if monthyear :
		num = monthyear.current_number + 1
	else :
		num = 1
		
	# Update generated number in DB
	gen_num = Generate_number_by_month(
		type = 'INVOICE-NUMBER',
		description = "Invoice number generation",
		month_year = mnth,
		current_number = num
		)
	
	gen_num.save()
		
	generated_num = 0
	if prefix:
		mnth = prefix + mnth
	if suffix:
		generated_num = (mnth + suffix + str(num))
	else:
		generated_num = (mnth + str(num))
	return generated_num 	

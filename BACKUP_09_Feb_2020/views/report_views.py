from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Sum

from datetime import datetime
import datetime

from artevenue.decorators import is_manager
from artevenue.models import Order, Order_items_view, Ecom_site

today = datetime.datetime.today()
ecom_site = Ecom_site.objects.get(store_id=settings.STORE_ID )

@csrf_exempt
@is_manager
def get_order_summary(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")

	order_list = Order.objects.all().order_by('invoice_date')
	
	order_items_list = {}
	if startDt:
		order_list = order_list.filter(order_date__gte = startDt)
	if endDt:
		order_list = order_list.filter(order_date__lte = endDt)
		
	#order_items_list = Order_items_view.objects.filter(
	#	order__in = order_list, product__product_type_id = F('product_type_id')).select_related('product', 'promotion')

	## Totals
	totals = order_list.aggregate(Sum('unit_price'), Sum('quantity'), Sum('order_discount_amt'), 
		Sum('shipping_cost'), Sum('sub_total'), Sum('tax'), Sum('order_total'))


	igst = order_list.exclude(order_billing__state__state_name__iexact=ecom_site.store_state).aggregate(igst=Sum('tax'))
	if igst:
		if igst['igst']:
			total_igst = igst['igst']
		else:
			total_igst = 0.0
	else:
		total_igst = 0.0

	cgst = order_list.filter(order_billing__state__state_name__iexact=ecom_site.store_state).aggregate(cgst=Sum('tax'))
	if cgst :
		if cgst['cgst']:
			total_cgst = cgst['cgst'] / 2
		else:
			total_cgst = 0.0
	else:
		total_cgst = 0.0
		
	total_sgst = total_cgst
	
	if printpdf == "YES":
		html_string = render_to_string('artevenue/order_summary_print.html', {
			'orders': order_list, 'totals':totals, 'startDt':startDt, 'endDt':endDt,
			'ecom_site':ecom_site, 'total_cgst':total_cgst, 'total_sgst':total_sgst,
			'total_igst':total_igst})

		html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
		
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_ord_pdf.pdf',
			stylesheets=[
						CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
						],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_ord_sum_pdf.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_ord_pdf.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/order_summary_table.html', { 
			'orders': order_list, 'totals':totals, 'startDt':startDt, 'endDt':endDt,
			'ecom_site':ecom_site, 'total_cgst':total_cgst, 'total_sgst':total_sgst,
			'total_igst':total_igst})		


def store_order_summary(request):
	return render(request, 'artevenue/store_order_summary.html')
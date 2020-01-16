from artevenue.models import Promotion, Voucher, Promotion_voucher

from django import template
from datetime import datetime
import datetime


today = datetime.date.today()

register = template.Library()
@register.inclusion_tag('artevenue/show_promo.html')
def promo_display(request):

	if request.user.is_authenticated:
		disp_promo = {}
	else:
		# Get promos from DB
		disp_promo = Promotion_voucher.objects.filter(
			promotion__effective_from__lte = today,
			promotion__effective_to__gte = today).first()
	return ({'disp_promo':disp_promo})

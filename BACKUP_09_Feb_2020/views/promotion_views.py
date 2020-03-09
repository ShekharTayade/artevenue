from django.shortcuts import render, get_object_or_404


def promotion_products(request):

	return render(request, "artevenue/promotion_select_products.html", {})
	
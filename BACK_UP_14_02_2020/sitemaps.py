from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticSitemap(Sitemap):
	priority = 0.8
	changefreq = 'weekly'

	def items(self):
		# Return list of url names for views to include in sitemap
		return ['index', 'about_us', 'my_account', 'my_orders', 'find_orders',
			'stock_image_detail', 'register', 'business_registration', 
			'contact_us', 'refer_us', 'egift_card', 'terms_conditions',
			'privacy_policy', 'faq', 'products_by_keywords', 'category_stock_images',
			'show_all_categories', 'all_stock_images', 'curated_collections', 'user_image',
			'show_cart', 'show_wishlist', 'user_collection', 'checkout_step1_address',
			'checkout_saveAddr_shippingMethod', 'checkout_step3_order_review',
			]

	def location(self, item):
		return reverse(item)


from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

from django.contrib.sitemaps.views import sitemap
from artevenue.sitemaps import *
sitemaps = {
   'static': StaticSitemap(),
}


urlpatterns = [
	
	url(r'^$', views.index, name='index'),	

	url(r'^accounts/', include('allauth.urls')),
	url(r'^login/$', views.artevenuelogin, name='login'),	
	url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),

	url(r'^password/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),    
	url(r'^password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),

	url(r'^reset/$', auth_views.PasswordResetView.as_view(
		template_name='password_reset.html',
		email_template_name='password_reset_email.html',
		subject_template_name='password_reset_subject.txt'), name='password_reset'),
	url(r'^reset/done/$', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
	url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
	   auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
	   name='password_reset_confirm'),
	url(r'^reset/complete/$',
	   auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
	   name='password_reset_complete'), 

	url(r'^my-account/$', views.my_account, name='my_account'),	
	url(r'^my-orders/$', views.my_orders, name='my_orders'),	
	url(r'^ajax/get_orders/$', views.get_orders, name='get_orders'),	
	#url(r'^order_pdf/$', views.get_orders, name='get_orders'),
	url(r'^store-orders/$', views.store_orders, name='store_orders'),	
	url(r'^ajax/get_store_orders/$', views.get_store_orders, name='get_store_orders'),	
	url(r'^store-order-pdf/$', views.get_store_orders, name='get_store_orders'),
	url(r'^find-orders/$', views.find_orders, name='find_orders'),	
	url(r'^update-orders/$', views.get_orders_for_status_update, name='get_orders_for_status_update'),
	url(r'^ajax/update_order_status/$', views.update_order_status, name='update_order_status'),

	url(r'^store-invoices/$', views.store_invoices, name='store_invoices'),	
	url(r'^ajax/get_invoices/$', views.get_invoices, name='get_invoices'),	

	url(r'^store-carts/$', views.store_carts, name='store_carts'),	
	url(r'^ajax/get_carts/$', views.get_carts, name='get_carts'),	

	url(r'^homelane-products/$', views.homelane_products, name='homelane_products'),
	url(r'^amazon-products/$', views.amazon_products, name='amazon_products'),	
	url(r'^sign-up/$', views.register, name='register'),
	path('sign-up/<int:signup_popup>', views.register, name='register'),

	url(r'^newsletter-subscription/$', views.newsletter_subscription_confirmation, name='newsletter_subscription'),


	url(r'^business-registration/$', views.business_registration, name='business_registration'),	
	url(r'^pending-business-accounts/$', views.pending_business_accounts, name='pending_business_accounts'),
	url(r'^business-account-approval/$', views.business_account_approval, name='business_account_approval'),
	url(r'^send-business-account-approval_email/$', views.send_business_account_approval_email, name='send_business_account_approval_email'),

	url(r'^promotion-products/$', views.promotion_products, name='promotion_products'),

	url(r'^current-offers/$', views.offers, name='offers'),

	url(r'^contact-us/$', views.contact_us, name='contact_us'),	
	url(r'^contact-msg/$', views.contact_msg, name='contact_msg'),	

	url(r'^refer-us/$', views.refer_us, name='refer_us'),	
	path('refer-confirm/<int:ref_id>/', views.refer_confirm, name='refer_confirm'),	

	url(r'^egift-card/$', views.egift_card, name='egift_card'),	
	path('egift-card-review/<int:gift_rec_id>/', views.egift_card_review, name='egift_card_review'),	
	#path('refer_confirm/<int:ref_id>/', views.refer_confirm, name='refer_confirm'),	
	url(r'^egift-payment-details/$', views.egift_payment_details, name='egift_payment_details'),	
	url(r'^egift-payment-submit/$', views.egift_payment_submit, name='egift_payment_submit'),
	url(r'^egift-payment-done/$', views.egift_payment_done, name='egift_payment_done'),		
	path('send-egift-mail/<int:gift_rec_id>/', views.send_egift_mail, name='send_egift_mail'),
	url(r'^egift-payment-unsuccessful/$', views.egift_payment_unsuccessful, name='egift_payment_unsuccessful'),		
	
	url(r'^about-us/$', views.about_us, name='about_us'),
	url(r'^terms-conditions/$', views.terms_conditions, name='terms_conditions'),
	url(r'^privacy-policy/$', views.privacy_policy, name='privacy_policy'),
	url(r'^faq/$', views.faq, name='faq'),

	url(r'^product/$', views.stock_image_detail, name='stock_image_detail'),	
	path('product/<int:prod_id>/', views.stock_image_detail, name='stock_image_detail'),	
	path('product/<int:prod_id>/<int:iuser_width>/<int:iuser_height>', views.stock_image_detail, name='stock_image_detail'),
	url(r'^products-by-keywords/$', views.search_products_by_keywords, name='art_by_category'),
	url(r'^art-by-category/$', views.get_stock_images, name='art_by_category'),
	path('art-by-category/<str:cat_nm>/', views.get_stock_images, name='art_by_category'),
	path('art-by-category/<str:cat_nm>/<int:page>', views.get_stock_images, name='art_by_category'),
	path('art-by-category/<int:cat_id>/', views.get_stock_images, name='art_by_category'),
	path('art-by-category/<int:cat_id>/<int:page>', views.get_stock_images, name='art_by_category'),
	path('art-by-category/cat_id=<int:cat_id>/page=<int:page>', views.get_stock_images, name='art_by_category'),
	url(r'^category-stock-images/$', views.category_stock_images, name='category_stock_images'),
	path('category-stock-images/<int:cat_id>/', views.category_stock_images, name='category_stock_images'),
	path('category-stock-images/<int:cat_id>/<int:page>', views.category_stock_images, name='category_stock_images'),

	path('product-original-art/<int:prod_id>/', views.original_art_detail, name='original_art_detail'),	
	url(r'^original-art-by-category/$', views.original_art_by_category, name='original_art_by_category'),
	path('original-art-by-category/<int:cat_id>/', views.original_art_by_category, name='original_art_by_category'),
	path('original-art-by-category/<int:cat_id>/<int:page>', views.original_art_by_category, name='original_art_by_category'),

	url(r'^ajax/get-catalog-card/$', views.get_catalog_card, name='get_catalog_card'),
	
	url(r'^show-all-categories/$', views.show_categories, name='show_all_categories'),
	#url(r'^all_images/$', views.all_stock_images, name='all_stock_images'),
	url(r'^all-art-images/$', views.get_stock_images, name='all_art_images'),
	url(r'^curated-collections/$', views.curated_collections, name='curated_collections'),
	path('curated-collections/<str:cat_nm>/', views.curated_collections, name='curated_collections'),
	path('curated-collections/<str:cat_nm>/<int:page>', views.curated_collections, name='curated_collections'),
	path('curated-collections/<int:cat_id>/', views.curated_collections, name='curated_collections'),	
	path('curated-collections/<str:cat_nm>/<int:page>/<int:prod_id>', views.curated_collections, name='curated_collections'),
	path('curated-collections/<int:cat_id>/<int:prod_id>', views.curated_collections, name='curated_collections'),
	url(r'^image-by-image-code/$', views.image_by_image_code, name='image_by_image_code'),

	url(r'^custom-framing/$', views.user_image, name='user_image'),
	url(r'^ajax/get_user_image_id/$', views.get_user_image_id, name='get_user_image_id'),
	url(r'^ajax/upload_user_image/$', views.upload_user_image, name='upload_user_image'),
	url(r'^ajax/show_mouldings_for_user_image/$', views.show_mouldings_for_user_image, name='show_mouldings_for_user_image'),
	url(r'^ajax/get_FramedUserImage/$', views.get_FramedUserImage, name='get_FramedUserImage'),
	url(r'^ajax/get_FramedUserImage_by_id/$', views.get_FramedUserImage_by_id, name='get_FramedUserImage_by_id'),
	url(r'^ajax/remove_user_image/$', views.remove_user_image, name='remove_user_image'),
	url(r'^ajax/crop_user_image/$', views.crop_user_image, name='crop_user_image'),	


	url(r'^ajax/sync_cart_session_user/$', views.sync_cart_session_user, name='sync_cart_session_user'),
	url(r'^show-cart/$', views.show_cart, name='show_cart'),
	url(r'^ajax/add_to_cart/$', views.add_to_cart_new, name='add_to_cart'),
	url(r'^ajax/delete_cart_item/$', views.delete_cart_item, name='delete_cart_item'),
	url(r'^ajax/update_cart_item/$', views.add_to_cart_new, name='update_cart_item'),
	url(r'^ajax/apply_voucher/$', views.apply_voucher, name='apply_voucher'),

	url(r'^ajax/show_mouldings/$', views.show_mouldings, name='show_mouldings'),

	url(r'^ajax/add_to_wishlist/$', views.add_to_wishlist, name='add_to_wishlist'),
	url(r'^show-wishlist/$', views.show_wishlist, name='show_wishlist'),
	url(r'^ajax/delete_wishlist_item/$', views.delete_wishlist_item, name='delete_wishlist_item'),
	url(r'^ajax/move_item_to_cart/$', views.move_item_to_cart, name='move_item_to_cart'),
	url(r'^ajax/move_all_to_cart/$', views.move_all_to_cart, name='move_all_to_cart'),
	
	url(r'^user-collection/$', views.user_collection, name='user_collection'),
	path('user-collection/<int:user_collection_id>/', views.user_collection, name='user_collection'),
	url(r'^ajax/move_to_collection/$', views.move_to_collection, name='move_to_collection'),
	url(r'^ajax/move_to_space/$', views.move_to_space, name='move_to_space'),
	url(r'^ajax/remove_from_collection/$', views.remove_from_collection, name='remove_from_collection'),
	url(r'^ajax/remove_from_space/$', views.remove_from_space, name='remove_from_space'),
	url(r'^ajax/create_collection/$', views.create_collection, name='create_collection'),
	url(r'^create-space/$', views.create_space, name='create_space'),
	url(r'^ajax/remove_collection/$', views.remove_collection, name='remove_collection'),
	url(r'^ajax/remove_space/$', views.remove_space, name='remove_space'),

	url(r'^ajax/get_moulding_price/$', views.get_moulding_price, name='get_moulding_price'),
	url(r'^ajax/get_mount_price/$', views.get_mount_price, name='get_mount_price'),
	url(r'^ajax/get_board_price/$', views.get_board_price, name='get_board_price'),
	url(r'^ajax/get_acrylic_price/$', views.get_acrylic_price, name='get_acrylic_price'),
	url(r'^ajax/get_item_price/$', views.get_item_price, name='get_item_price'),
	url(r'^ajax/get_FramedImage/$', views.get_FramedImage, name='get_framed_image'),
	url(r'^ajax/get_FramedUserImage_by_id/$', views.get_FramedUserImage_by_id, name='get_FramedUserImage_by_id'),
	#url(r'^ajax/apply_voucher/$', views.apply_voucher, name='apply_voucher'),

	url(r'^checkout-step1/$', views.checkout_step1_address, name='checkout_step1_address'),
	url(r'^checkout-step2/$', views.checkout_saveAddr_shippingMethod, name='checkout_saveAddr_shippingMethod'),
	url(r'^checkout-step3/$', views.checkout_step3_order_review, name='checkout_step3_order_review'),


	url(r'^ajax/get_addr_pin_city_state/$', views.get_addr_pin_city_state, name='get_addr_pin_city_state'),
	url(r'^ajax/validate_address/$', views.validate_address, name='validate_address'),

	url(r'^payment-details/$', views.payment_details, name='payment_details'),
	url(r'^payment-submit/$', views.payment_submit, name='payment_submit'),
	url(r'^payment-done/$', views.payment_done, name='payment_done'),
	url(r'^payment-unsuccessful/$', views.payment_unsuccessful, name='payment_unsuccessful'),

	url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),	

	url(r'^store-order-summary/$', views.store_order_summary, name='store_order_summary'),	
	url(r'^ajax/get_order_summary/$', views.get_order_summary, name='get_order_summary'),	
	
	url(r'^manage-amazon-orders/$', views.amazon_orders_manage, name='amazon_orders_manage'),
	url(r'^amazon-enter-new-order/$', views.amazon_enter_new_order, name='amazon_enter_new_order'),
	url(r'^ajax/amazon_order_details/$', views.amazon_order_details, name='amazon_order_details'),	
	url(r'^ajax/get_amz_orders/$', views.get_amz_orders, name='get_amz_orders'),	
	
	url(r'^ajax/get_ready_products/$', views.get_ready_products, name='get_ready_products'),	

	url(r'^ajax/my-business-report/$', views.my_business_report, name='my_business_report'),
	url(r'^my-business-report/$', views.my_business_report_wrap, name='my_business_report_wrap'),	
	path('my-client-order-report/<int:client_id>/', views.my_client_order_report, name='my_client_order_report'),

	url(r'^artprint-sets/$', views.stock_collage_products, name='stock_collage_products'),
	url(r'^ajax/get-framed-collage/$', views.get_framed_collage, name='get_framed_collage'),
	url(r'^ajax/get-collage-price/$', views.get_collage_price, name='get_collage_price'),
	url(r'^artprint-set/$', views.stock_collage_detail, name='stock_collage_detail'),
	path('artprint-set/<int:prod_id>/', views.stock_collage_detail, name='stock_collage_detail'),	
	path('artprint-set/<int:prod_id>/<int:iuser_width>/<int:iuser_height>', views.stock_collage_detail, name='stock_collage_detail'),
	url(r'^ajax/get-collage-catalog-card/$', views.get_collage_catalog_card, name='get_collage_catalog_card'),
		 
	url(r'^ajax/show-on-wall/$', views.show_on_wall, name='show_on_wall'),
	url(r'^ajax/show-on-wall-set/$', views.show_on_wall_set, name='show_on_wall_set'),

	url(r'^how-to-customize-art-print/', views.how_to_customize, name='how_to_customize'),	

	url(r'^how-to-hang-art/', views.how_to_hang, name='how_to_hang'),	

	] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


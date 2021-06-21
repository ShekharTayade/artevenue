
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

	url(r'^cart_order_match_report/$', views.cart_order_match_report, name='cart_order_match_report'),
	url(r'^ajax/get_cart_order_match/$', views.get_cart_order_match, name='get_cart_order_match'),	

	url(r'^store-carts/$', views.store_carts, name='store_carts'),	
	url(r'^ajax/get_carts/$', views.get_carts, name='get_carts'),	

	#url(r'^homelane-products/$', views.homelane_products, name='homelane_products'),
	url(r'^amazon-products/$', views.amazon_products, name='amazon_products'),	
	
	
	url(r'^sign-up/$', views.register, name='register'),
	path('sign-up/<int:signup_popup>', views.register, name='register'),


	url(r'^livspace-login/$', views.livspace_login, name='livspace_login'),	
	url(r'^livspace-register/$', views.livspace_register, name='livspace_register'),
	url(r'^livspace-accounts-of-designers/$', views.livspace_accounts_of_designers, name='livspace_accounts_of_designers'),	
	url(r'^ajax/remove-liv-accnt/$', views.remove_liv_accnt, name='remove_liv_accnt'),
	url(r'^livspace-login-invalid/$', views.livspace_login_error, name='livspace_login_error'),
	url(r'^livspace-login-error/$', views.livspace_login_error, name='livspace_login_error'),
	url(r'^livspace-login-test/$', views.livspace_login_test, name='livspace_login_test'),
		

	url(r'^newsletter-subscription/$', views.newsletter_subscription_confirmation, name='newsletter_subscription'),


	url(r'^business-registration/$', views.business_registration, name='business_registration'),	
	url(r'^pending-business-accounts/$', views.pending_business_accounts, name='pending_business_accounts'),
	url(r'^business-account-approval/$', views.business_account_approval, name='business_account_approval'),
	url(r'^send-business-account-approval_email/$', views.send_business_account_approval_email, name='send_business_account_approval_email'),

	url(r'^promotion-products/$', views.promotion_products, name='promotion_products'),

	url(r'^offers-on-wall-art/$', views.offers, name='offers'),

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

	url(r'^art-print/$', views.stock_image_detail, name='stock_image_detail'),	
	path('art-print/<int:prod_id>/', views.stock_image_detail, name='stock_image_detail'),	
	path('art-print/<int:prod_id>/<int:iuser_width>/<int:iuser_height>', views.stock_image_detail, name='stock_image_detail'),
	url(r'^art-prints-by-keywords/$', views.search_products_by_keywords, name='art_by_category'),
	url(r'^art-prints/$', views.get_stock_images, name='art_by_category'),
	path('art-prints/<str:cat_nm>/', views.get_stock_images, name='art_by_category'),
	path('art-prints/<str:cat_nm>/<int:page>', views.get_stock_images, name='art_by_category'),
	path('art-prints/<int:cat_id>/', views.get_stock_images, name='art_by_category'),
	path('art-prints/<int:cat_id>/<int:page>', views.get_stock_images, name='art_by_category'),
	path('art-prints/cat_id=<int:cat_id>/page=<int:page>', views.get_stock_images, name='art_by_category'),
	url(r'^category-stock-images/$', views.category_stock_images, name='category_stock_images'),
	path('category-stock-images/<int:cat_id>/', views.category_stock_images, name='category_stock_images'),
	path('category-stock-images/<int:cat_id>/<int:page>', views.category_stock_images, name='category_stock_images'),

	url(r'^ajax/get-catalog-card/$', views.get_catalog_card, name='get_catalog_card'),
	
	url(r'^show-all-wall-art-categories/$', views.show_categories, name='show_all_categories'),
	#url(r'^all_images/$', views.all_stock_images, name='all_stock_images'),
	url(r'^all-art-images/$', views.get_stock_images, name='all_art_images'),
	url(r'^curated-art-prints/$', views.curated_collections, name='curated_collections'),
	path('curated-art-prints/<str:cat_nm>/', views.curated_collections, name='curated_collections'),
	path('curated-art-prints/<str:cat_nm>/<int:page>', views.curated_collections, name='curated_collections'),
	path('curated-art-prints/<int:cat_id>/', views.curated_collections, name='curated_collections'),	
	path('curated-art-prints/<str:cat_nm>/<int:page>/<int:prod_id>', views.curated_collections, name='curated_collections'),
	path('curated-art-prints/<int:cat_id>/<int:prod_id>', views.curated_collections, name='curated_collections'),
	url(r'^image-by-image-code/$', views.image_by_image_code, name='image_by_image_code'),

	#url(r'^abstract-paintings/$', views.category_landing_page, name='category_landing_page'),


	url(r'^custom-photo-frames/$', views.user_image, name='user_image'),
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
	url(r'^ajax/delete_cart/$', views.delete_cart, name='delete_cart'),

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
	url(r'^order-confirmation/$', views.payment_done, name='payment_done'),
	url(r'^payment-unsuccessful/$', views.payment_unsuccessful, name='payment_unsuccessful'),

	url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),	

	url(r'^store-order-summary/$', views.store_order_summary, name='store_order_summary'),	
	url(r'^ajax/get_order_summary/$', views.get_order_summary, name='get_order_summary'),	
	
	#url(r'^manage-amazon-orders/$', views.amazon_orders_manage, name='amazon_orders_manage'),
	#url(r'^amazon-enter-new-order/$', views.amazon_enter_new_order, name='amazon_enter_new_order'),	
	#url(r'^ajax/amazon_order_details/$', views.amazon_order_details, name='amazon_order_details'),	
	#url(r'^ajax/get_amz_orders/$', views.get_amz_orders, name='get_amz_orders'),	
	
	url(r'^ajax/get_ready_products/$', views.get_ready_products, name='get_ready_products'),	

	url(r'^ajax/my-business- report/$', views.my_business_report, name='my_business_report'),
	url(r'^my-business-report/$', views.my_business_report_wrap, name='my_business_report_wrap'),	
	path('my-client-order-report/<int:client_id>/', views.my_client_order_report, name='my_client_order_report'),

	url(r'^wall-art-collage-sets/$', views.stock_collage_products, name='stock_collage_products'),
	###########################################################
	######################## WHEN SETS IS DONE
	url(r'^wall-art-sets/$', views.wall_art_set_products, name='stock_collage_products'),
	path('wall-art-sets/set-of-<str:set_of>-wall-art/', views.wall_art_set_products, name='stock_collage_products'),
	path('wall-art-sets/<str:print_medium>-wall-art-sets/', views.wall_art_set_products, name='stock_collage_products'),
	###########################################################
	
	url(r'^framed-wall-art/$', views.wall_art_set_products, name='framed_wall_art_collection'),
	path('framed-wall-art/framed-<str:print_medium>-wall-art/', views.wall_art_set_products, name='framed_wall_art_by_surface'),
	
	url(r'^ajax/get-framed-collage/$', views.get_framed_collage, name='get_framed_collage'),
	url(r'^ajax/get-collage-price/$', views.get_collage_price, name='get_collage_price'),
	#url(r'^wall-art-collage-set/$', views.stock_collage_detail, name='stock_collage_detail'),
	#path('wall-art-collage-set/<int:prod_id>/', views.stock_collage_detail, name='stock_collage_detail'),	
	url(r'^wall-art-collage-set/$', views.set_detail, name='stock_collage_detail'),
	path('wall-art-collage-set/<int:prod_id>/', views.set_detail, name='stock_collage_detail'),	
	#path('wall-art-collage-set/<int:prod_id>/<int:iuser_width>/<int:iuser_height>', views.stock_collage_detail, name='stock_collage_detail'),

	path('framed-wall-art/<int:prod_id>/', views.set_detail, name='framed_wall_art'),	


	url(r'^ajax/get-collage-catalog-card/$', views.get_collage_catalog_card, name='get_collage_catalog_card'),
		 
	url(r'^ajax/show-on-wall/$', views.show_on_wall, name='show_on_wall'),
	url(r'^ajax/show-on-wall-set/$', views.show_on_wall_set, name='show_on_wall_set'),

	url(r'^how-to-customize-a-painting/', views.how_to_customize, name='how_to_customize'),	
	url(r'^how-to-hang-a-painting/', views.how_to_hang, name='how_to_hang'),	
	url(r'^how-to-select-painting-size/', views.how_to_size, name='how_to_size'),

	url(r'^order-management/', views.order_management, name='order_management'),	
	url(r'^manage-order-details/', views.manage_order_details, name='manage_order_details'),	
	path('order-address-change/<int:order_id>', views.order_addr_change, name='order_addr_change'),
	path('order-address-change-confirm/<int:order_id>', views.order_addr_change_confirm, name='order_addr_change_confirm'),
	#path('order-modify-items/<int:order_id>', views.order_modify_items, name='order_modify_items'),

	url(r'^start-production/', views.start_production, name='start_production'),
	url(r'^ajax/set-in-production/$', views.set_in_production, name='set_in_production'),
	url(r'^make-ready-for-shipping/', views.make_ready_for_shipping, name='make_ready_for_shipping'),
	url(r'^ajax/set-ready-for-shipping/$', views.set_ready_for_shipping, name='set_ready_for_shipping'),
	url(r'^order-shipping/', views.order_shipping, name='order_shipping'),
	url(r'^ajax/make-in-transit/$', views.make_in_transit, name='make_in_transit'),
	url(r'^order-dashboard/', views.order_dashboard, name='order_dashboard'),
	path('print-pf-labels/<int:order_id>', views.print_pf_labels, name='print_pf_labels'),
	url(r'^order-delivery/', views.order_delivery, name='order_delivery'),
	url(r'^ajax/set-order-delivery/$', views.set_order_delivery, name='set_order_delivery'),


	url(r'^staff-page/', views.staff_page, name='staff_page'),	
	url(r'^generate-shipping-template/', views.generate_shipping_template, name='generate_shipping_template'),	
	url(r'^ajax/shipping-template-table/$', views.get_orders_for_shipping_template, name='get_orders_for_shipping_template'),

	url(r'^coupon-management/', views.coupon_management, name='coupon_management'),	
	url(r'^apply-coupon/', views.apply_coupon, name='apply_coupon'),	
	url(r'^ajax/after-coupon-view/$', views.after_coupon_view, name='after_coupon_view'),
	url(r'^ajax/apply-coupon-code/$', views.apply_coupon_code, name='apply_coupon_code'),

	url(r'^invoice-report/', views.invoice_report, name='invoice_report'),	
	url(r'^get-invoice-report/', views.get_invoice_report, name='get_invoice_report'),	

	url(r'^print-pf-labels/$', views.pf_label_bulk, name = "pf_label_bulk"),
	url(r'^print-bulk-pf-labels/$', views.print_bulk_pf_labels, name='print_bulk_pf_labels'),



	url(r'^create-set-single/', views.create_set_single, name='create_set_single'),	
	url(r'^set-single-data/', views.set_single_data, name='set_single_data'),	
	url(r'^ajax/get-product/$', views.get_product, name='get_product'),
	url(r'^ajax/save-new-set-single/$', views.save_new_set_single, name='save_new_set_single'),
	url(r'^generate-set-prices/', views.generate_set_prices, name='generate_set_prices'),
	url(r'^ajax/create_initial_data/$', views.createInitialData, name='createInitialData'),

	
	] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


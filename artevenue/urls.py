
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

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
	
    url(r'^my_account/$', views.my_account, name='my_account'),	
    url(r'^my_orders/$', views.my_orders, name='my_orders'),	
    url(r'^ajax/get_orders/$', views.get_orders, name='get_orders'),	
    url(r'^order_pdf/$', views.get_orders, name='get_orders'),
	url(r'^store_orders/$', views.store_orders, name='store_orders'),	
	url(r'^ajax/get_store_orders/$', views.get_store_orders, name='get_store_orders'),	
	url(r'^store_order_pdf/$', views.get_store_orders, name='get_store_orders'),

	url(r'^import_image_data/$', views.importImageData_NEW, name='import_image_data'),

	
    url(r'^register/$', views.register, name='register'),	
    url(r'^business_registration/$', views.business_registration, name='business_registration'),	
	url(r'^pending_business_accounts/$', views.pending_business_accounts, name='pending_business_accounts'),
	url(r'^business_account_approval/$', views.business_account_approval, name='business_account_approval'),

	url(r'^promotion_products/$', views.promotion_products, name='promotion_products'),

	
    url(r'^contact_us/$', views.contact_us, name='contact_us'),	
    url(r'^contact_msg/$', views.contact_msg, name='contact_msg'),	
	
    url(r'^about_us/$', views.about_us, name='about_us'),
    url(r'^terms_conditions/$', views.terms_conditions, name='terms_conditions'),
	url(r'^faq/$', views.faq, name='faq'),



	path('product/<int:prod_id>/', views.stock_image_detail, name='stock_image_detail'),	
    url(r'^products_by_keywords/$', views.search_products_by_keywords, name='products_by_keywords'),
	path('category_stock_images/<int:cat_id>/', views.category_stock_images, name='category_stock_images'),
	url(r'^show_all_categories/$', views.show_categories, name='show_all_categories'),
	
    url(r'^user_image/$', views.user_image, name='user_image'),
 	url(r'^ajax/get_user_image_id/$', views.get_user_image_id, name='get_user_image_id'),
	url(r'^ajax/upload_user_image/$', views.upload_user_image, name='upload_user_image'),
	url(r'^ajax/show_mouldings_for_user_image/$', views.show_mouldings_for_user_image, name='show_mouldings_for_user_image'),
 	url(r'^ajax/get_FramedUserImage/$', views.get_FramedUserImage, name='get_FramedUserImage'),
 	url(r'^ajax/get_FramedUserImage_by_id/$', views.get_FramedUserImage_by_id, name='get_FramedUserImage_by_id'),
	
	url(r'^ajax/sync_cart_session_user/$', views.sync_cart_session_user, name='sync_cart_session_user'),
    url(r'^show_cart/$', views.show_cart, name='show_cart'),
	url(r'^ajax/add_to_cart/$', views.add_to_cart, name='add_to_cart'),
	url(r'^ajax/delete_cart_item/$', views.delete_cart_item, name='delete_cart_item'),
	url(r'^ajax/update_cart_item/$', views.update_cart_item, name='update_cart_item'),
 	url(r'^ajax/apply_voucher/$', views.apply_voucher, name='apply_voucher'),


	url(r'^ajax/show_mouldings/$', views.show_mouldings, name='show_mouldings'),
	#url(r'^ajax/get_addr_pin_city_state/$', views.get_addr_pin_city_state, name='get_addr_pin_city_state'),
	#url(r'^ajax/validate_address/$', views.validate_address, name='validate_address'),
	
	
	url(r'^ajax/add_to_wishlist/$', views.add_to_wishlist, name='add_to_wishlist'),
    url(r'^show_wishlist/$', views.show_wishlist, name='show_wishlist'),
	#url(r'^ajax/delete_wishlist_item/$', views.delete_wishlist_item, name='delete_wishlist_item'),

	
	url(r'^ajax/get_moulding_price/$', views.get_moulding_price, name='get_moulding_price'),
 	url(r'^ajax/get_mount_price/$', views.get_mount_price, name='get_mount_price'),
 	url(r'^ajax/get_board_price/$', views.get_board_price, name='get_board_price'),
 	url(r'^ajax/get_acrylic_price/$', views.get_acrylic_price, name='get_acrylic_price'),
 	url(r'^ajax/get_item_price/$', views.get_item_price, name='get_item_price'),
 	url(r'^ajax/get_FramedImage/$', views.get_FramedImage, name='get_framed_image'),
 	url(r'^ajax/get_FramedUserImage_by_id/$', views.get_FramedUserImage_by_id, name='get_FramedUserImage_by_id'),
 	#url(r'^ajax/apply_voucher/$', views.apply_voucher, name='apply_voucher'),
	
	url(r'^checkout_step1/$', views.checkout_step1_address, name='checkout_step1_address'),
	url(r'^checkout_step2/$', views.checkout_saveAddr_shippingMethod, name='checkout_saveAddr_shippingMethod'),
	url(r'^checkout_step3/$', views.checkout_step3_order_review, name='checkout_step3_order_review'),
	

	url(r'^ajax/get_addr_pin_city_state/$', views.get_addr_pin_city_state, name='get_addr_pin_city_state'),
	url(r'^ajax/validate_address/$', views.validate_address, name='validate_address'),


	
	] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


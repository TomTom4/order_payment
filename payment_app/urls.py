from django.conf.urls import url
from django.contrib.auth.views import login

from . import views

urlpatterns = [
	url(r'^accounts/login/$', login, {'template_name': 'admin/login.html'}),
	url(r'^$', views.show_register_form, name='register'),
	
	url(r'^merchandise_details/(?P<product_id>[0-9]+)/$', views.merchandise_details, name='merchandise_details'),
	url(r'^purchase/(?P<product_id>[0-9]+)/$', views.purchase, name='purchase'),
	url(r'^order/$', views.order, name='order'),
	url(r'^create_order/$', views.create_order, name='create_order'),
	url(r'^my_profile/$', views.my_profile, name='my_profile'),
	url(r'^payment/(?P<order_id>[0-9]+)/$', views.payment, name ='payment'),
	url(r'^cancel_all_purchases/$', views.cancel_all_purchases, name="cancel_all_purchases"),
	url(r'^cancel_purchase/(?P<purchase_id>[0-9]+)/$', views.cancel_purchase, name="cancel_purchase"),
	url(r'^create_sku_on_stripe/(?P<product_id>[0-9]+)/$', views.create_sku_form, name="create_sku_on_stripe"),
	url(r'^create_sku/(?P<ids>([0-9]*,?[0-9])*)/$', views.create_sku, name="create_sku_display"),
	url(r'^display_sku/(?P<ids>([0-9]*,?[0-9])*)/$', views.display_sku, name="display_sku"),
	url(r'^lower_sku_quantity/(?P<sku_id>sku_.*)/$', views.lower_sku_quantity, name="lower_sku_quantity"), 
	url(r'^delete_sku/(?P<sku_id>sku_.*)/$', views.delete_sku, name="delete_sku"), 
	url(r'^delete_product/(?P<product_id>[0-9]+)/$', views.delete_product, name='delete_product'),
	url(r'^handle_order_status/(?P<ids>([0-9]*,?[0-9])*)/$', views.handle_order_status, name="handle_order_status"),
	url(r'^update_order_status/(?P<order_id>[0-9]+)/$', views.update_order_status, name='update_order_status'),


	]



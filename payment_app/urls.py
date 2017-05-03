from django.conf.urls import url
from django.contrib.auth.views import login

from . import views

urlpatterns = [
	url(r'^accounts/login/$', login, {'template_name': 'admin/login.html'}),
	url(r'^$', views.store, name='store'),
	url(r'^merchandise_details/(?P<product_id>[0-9]+)/$', views.merchandise_details, name='merchandise_details'),
	url(r'^purchase/(?P<product_id>[0-9]+)/$', views.purchase, name='purchase'),
	url(r'^pay_page/$', views.index, name='pay_page'),
	url(r'^payment/$', views.payment, name ='payment'),
	url(r'^cancel_all_purchases/$', views.cancel_all_purchases, name="cancel_all_purchases"),
	url(r'^cancel_purchase/(?P<purchase_id>[0-9]+)/$', views.cancel_purchase, name="cancel_purchase"),
	url(r'^create_sku_on_stripe/(?P<product_id>[0-9]+)/$', views.create_sku_form, name="create_sku_on_stripe"),
	url(r'^create_sku/(?P<ids>([0-9]*,?[0-9])*)/$', views.create_sku, name="create_sku_display"),
	url(r'^display_sku/(?P<ids>([0-9]*,?[0-9])*)/$', views.display_sku, name="display_sku"),
	url(r'^lower_sku_quantity/(?P<sku_id>sku_.*)/$', views.lower_sku_quantity, name="lower_sku_quantity"), 
	url(r'^delete_sku/(?P<sku_id>sku_.*)/$', views.delete_sku, name="delete_sku"), 
	url(r'^delete_product/(?P<product_id>[0-9]+)/$', views.delete_product, name='delete_product'),

	]



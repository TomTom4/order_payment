from django.contrib import admin
from django.shortcuts import redirect
from .models import *
import stripe
import json
from order_payment.settings import STRIPE_SECRET_KEY

admin.site.register(Purchase)
admin.site.register(Order)
# Register your models here.


class ProductAdmin(admin.ModelAdmin):

	actions = ['create_on_stripe','create_a_sku', 'display_sku']

	def create_on_stripe(self, request, queryset):
		counter = 0
		stripe.api_key = STRIPE_SECRET_KEY
		for a_product in queryset:
			if a_product.stripe_identifier is None or a_product.stripe_identifier == "":
				counter += 1
				attribute_list =list(json.loads(a_product.attribute_dict).keys())
				# Create the product
				response = stripe.Product.create(
				name= a_product.name,
				description=a_product.description,
				# These are the characteristics of the product that SKUs provide values for
				attributes= attribute_list
				)
				# retrieve stripe_key and update the product with
				a_product.stripe_identifier = response['id']
				a_product.save()
		if counter == 1:
			part_message = "1 product was"
		else:
			part_message = "{0} products were".format(counter)
		self.message_user(request, part_message + " successfully created on stripe's database")
			
	create_on_stripe.short_description = "Create the product on stripe's database"

	# here an action to create sku on stripe's db	
	def create_a_sku(self, request, queryset):
		selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		return redirect('create_sku_display',ids= ",".join(selected))
	create_a_sku.short_description = "Create or update specific SKUs"

	# useful for updates, and suppressions
	def display_sku(self, request, queryset):
		selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		return redirect('display_sku',ids = ",".join(selected))
	display_sku.short_description = "Retrieve and display all existing SKU"

admin.site.register(Product, ProductAdmin)

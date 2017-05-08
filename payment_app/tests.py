from django.test import TestCase
from .models import *
from .views import *
import stripe

PUBLISHABLE_KEY = "pk_test_6pRNASCoBOKtIshFeQd4XMUh"
SECRET_KEY = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

# Create your tests here.


class createOrderTestCase(TestCase):

	fixtures=['createOrder.json']

	def test_create_item_list_1_item(self):

		purchase_list = Purchase.objects.all()
		a_purchase = purchase_list[0]
		purchase_list =[ purchase_list[0]]
		a_product = a_purchase.product
	
		stripe.api_key = SECRET_KEY
		stripe_product = stripe.Product.create(
					name= a_product.name,
					description= a_product.description,
					attributes=list(a_product.get_attribute_dict_keys())
					)
		sku = stripe.SKU.create(
					product=stripe_product.id,
					attributes={
    							"size": "m",
  						},
  					price=1500,
  					currency="usd",
  					inventory={
    					"type": "finite",
    					"quantity": 5
  					}
					)
		a_product.stripe_identifier = stripe_product.id
		a_product.save()
		expected_output = [
					{
					"type":'sku',
					"parent":sku.id,
				 	"quantity":a_purchase.quantity
					}
				]
		item_list = create_item_list(purchase_list, stripe)
		self.assertListEqual(item_list, expected_output)
	
		# destroying every created stuff on stripe database to avoid side effects
		sku.delete()
		stripe_product.delete()

	def test_create_item_list_n_item(self):
		expected_output = list()
		stripe_products = list()
		stripe_skus = list()
		purchase_list = Purchase.objects.all()
		
		for a_purchase in purchase_list:
			a_product = a_purchase.product
	
			stripe.api_key = SECRET_KEY
			stripe_product = stripe.Product.create(
						name= a_product.name,
						description= a_product.description,
						attributes=list(a_product.get_attribute_dict_keys())
						)
			stripe_products.append(stripe_product)
			sku = stripe.SKU.create(
						product=stripe_product.id,
						attributes={
    								"size": "m",
  							},
  						price=1500,
  						currency="usd",
  						inventory={
    						"type": "finite",
    						"quantity": 5
  						}
					)
			stripe_skus.append(sku)
			a_product.stripe_identifier = stripe_product.id
			a_product.save()
			expected_output.append(
						{
						"type":'sku',
						"parent":sku.id,
				 		"quantity":a_purchase.quantity
						}
				)
		item_list = create_item_list(purchase_list, stripe)
		self.assertListEqual(item_list, expected_output)


		# destroying every created stuff on stripe database to avoid side effects
		for sku in stripe_skus:
			sku.delete()
		for stripe_product in stripe_products:
			stripe_product.delete()



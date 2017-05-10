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

class BucketTestCase(TestCase):
	fixtures = ['bucket.json']

	def test_query_all_unordered_purchases_1(self):
		user = User.objects.get(pk=1)
		Purchase.objects.get(pk=2).delete()
		expected_output = [Purchase.objects.get(pk=1)]
		output =list(query_all_unordered_purchases(user))
		self.assertListEqual(expected_output, output)

	def test_query_all_unordered_purchases_n(self):
		user = User.objects.get(pk=1)
		expected_output = [Purchase.objects.get(pk=1), Purchase.objects.get(pk=2)]
		output =list(query_all_unordered_purchases(user))
		self.assertListEqual(expected_output, output)

	def test_query_all_unordered_purchases_1_among_m(self):
		user = User.objects.get(pk=1)
		Purchase.objects.get(pk=2).delete()
		expected_output = [Purchase.objects.get(pk=1)]
		output =list(query_all_unordered_purchases(user))
		self.assertListEqual(expected_output, output)

	def test_query_all_unordered_purchases_n_among_m(self):
		user = User.objects.get(pk=1)
		expected_output = [Purchase.objects.get(pk=1), Purchase.objects.get(pk=2)]
		output =list(query_all_unordered_purchases(user))
		self.assertListEqual(expected_output, output)


class PurchaseTestCase(TestCase):
	fixtures=['purchase.json']

	def test_update_purchase_1_purchase(self):
		order = Order.objects.get(pk=1)
		purchase_list =list(Purchase.objects.all().filter(id = 1))

		update_purchase(purchase_list, order)

		for purchase in  Purchase.objects.all():
			if purchase.id == 1:
				self.assertEqual(purchase.order_identifier , order)
			else:
				self.assertNotEqual(purchase.order_identifier , order)

	def test_update_purchase_n_purchases(self):
		order = Order.objects.get(pk=1)
		purchase_list = list(Purchase.objects.all().filter(id__in =[1, 2, 3]))

		update_purchase(purchase_list, order)

		for purchase in  Purchase.objects.all():
			if purchase.id in [1,2,3]:
				self.assertEqual(purchase.order_identifier , order)
			else:
				self.assertNotEqual(purchase.order_identifier , order)



class CsvParsingTestCase(TestCase):
	
	def test_parse_simple_string(self):
		string = "1,2"
		self.assertListEqual(parse_csv_into_list(string),[1,2])

	def test_complex_string(self):
		string = '1, 2, 1, 3, 4, 5, 9, 78, 45658, 10, 16, 48997857, 12, 1111, 222222, 32, 1'
		expected_result = [1,2,1,3,4,5,9,78,45658,10,16,48997857,12,1111,222222,32,1]
		self.assertListEqual(parse_csv_into_list(string),expected_result)


# requires stripes database handling

class SkuHandlingTestCase(TestCase):
	
	stripe.api_key = SECRET_KEY
	fixtures = ['createOrder.json']
	
	class RequestFixture:

		def __init__(self, dic):
			self.POST = dic 
	

	# test when sku.quantity > request.POST['quantity']
	def test_udpate_sku_quantity_case_1(self):
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

		request = self.RequestFixture({'quantity': -2})
		update_sku_quantity(request, stripe_skus[0])
		self.assertEqual(stripe_skus[0].inventory['quantity'], 3)


		# destroying every created stuff on stripe database to avoid side effects
		for sku in stripe_skus:
			sku.delete()
		for stripe_product in stripe_products:
			stripe_product.delete()

	# test when sku.quantity <= request.POST['quantity']
	def test_udpate_sku_quantity_case_2(self):
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

		request = self.RequestFixture({'quantity': -6})
		update_sku_quantity(request, stripe_skus[0])
		self.assertEqual(stripe_skus[0].inventory['quantity'], 0)


		# destroying every created stuff on stripe database to avoid side effects
		for sku in stripe_skus:
			sku.delete()
		for stripe_product in stripe_products:
			stripe_product.delete()

class HandleSKUTestCase(TestCase):
	fixtures = ['createOrder.json']
	stripe.api_key = SECRET_KEY

	def test_find_chosen_sku_1(self):
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
			for size in ['s','m','l']:
				sku = stripe.SKU.create(
						product=stripe_product.id,
						attributes={
    								"size":size,
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
		print(stripe_skus[0:2])
		output = find_chosen_sku(stripe_skus[0:2],{"size":"m"})
		expected_output = stripe_skus[1]
		self.assertEqual(output, expected_output)

	def test_find_chosen_sku_2(self):
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
			for size in ['s','m','l']:
				sku = stripe.SKU.create(
						product=stripe_product.id,
						attributes={
    								"size":size,
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
		output = find_chosen_sku(stripe_skus[0:2],{'size':'x'})
		expected_output = None
		self.assertEqual(output, expected_output)


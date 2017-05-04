from django.shortcuts import render,redirect, get_list_or_404, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import stripe
from order_payment import settings
from .models import *
# Create your views here.


def store(request):
	# user = request.user
	user = User.objects.get(pk=1)
	product_list = get_list_or_404(Product, id__gte=1)
	try:
		purchased_list = get_list_or_404(Purchase, purchaser=user, order_identifier__isnull =True)
	except:
		purchased_list = None
	context = {'product_list':product_list,'purchased_list':purchased_list}
	return render(request,'payment_app/store.html', context)

def merchandise_details(request,product_id):
	product = get_object_or_404(Product, id = product_id)
	context = {'product': product}
	return render(request, 'payment_app/merchandise_details.html',context)

def purchase(request, product_id):
	# user = request.user
	# Dirty work should use the above instead ! ####################################################
	user = User.objects.get(pk=1)
	# *********************************************************************************************

	related_product = get_object_or_404(Product, id=product_id)
	a_purchase = Purchase(purchaser=user, product=related_product, quantity=request.POST['quantity'])
	a_dict = dict()

	for a_key in related_product.get_attribute_dict_keys():
		a_dict[a_key] = request.POST[a_key] 

	a_purchase.set_attribut_dict(a_dict)
	a_purchase.save()
	return redirect('store')

def cancel_all_purchases(request):
	# user = request.user
	user = User.objects.get(pk=1)
	Purchase.objects.all().filter(purchaser = user, order_identifier__isnull =True).delete()
	return redirect('store')

def cancel_purchase(request, purchase_id):
	# user = request.user
	user = User.objects.get(pk=1)
	Purchase.objects.get(pk = purchase_id).delete()
	return redirect('store')

def index(request):
	# user = request.user
	user = User.objects.get(pk=1)
	purchase_list = get_list_or_404(Purchase, purchaser=user, order_identifier__isnull =True)
	amount = 0
	for purchase in purchase_list:
		amount += purchase.product.price * purchase.quantity
	context = { 'amount' :amount, 'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
			'description':"bucket" } 
	return render(request, 'payment_app/pay_page.html', context)

def create_item_list( purchase_list, stripe):
	item_list = list()
	purchased_sku = None
	for a_purchase in purchase_list:
		sku_list = stripe.Product.retrieve(a_purchase.product.stripe_identifier).skus.data
		for a_sku in sku_list:
			if a_sku.attributes == a_purchase.get_attribut_dict():
				purchased_sku = a_sku	
		item_list.append({"type":'sku',	"parent":purchased_sku.id, "quantity":a_purchase.quantity})
	return item_list

def update_purchase(purchase_list, order):
	for a_purchase in purchase_list:
		a_purchase.order_identifier = order
		a_purchase.save()
		print(a_purchase.order_identifier)

def payment(request):
	# user = request.user
	user = User.objects.get(pk=1)
	purchase_list = get_list_or_404(Purchase, purchaser=user, order_identifier__isnull=True)
	stripe.api_key = settings.STRIPE_SECRET_KEY
	order = stripe.Order.create(currency = settings.CURRENCY,
					email = request.POST['stripeEmail'] ,
					items = create_item_list(purchase_list, stripe),
					shipping = {
					"name":request.POST['firstname']+' '+request.POST['lastname'],
					"address":{
					"line1":request.POST['address'],
					"city":request.POST['city'],
					"country":request.POST['country'],
					"postal_code":request.POST['postal_code']
					}
					},
				)
	modelOrder = Order(stripe_identifier=order.id , total_price = request.POST['amount'])
	modelOrder.save()
	update_purchase(purchase_list, modelOrder)
	print(order)
	order.pay(source = request.POST['stripeToken'])
	return redirect('store')

def create_sku(request, ids):
	id_list = [int(pk) for pk in ids.split(',')]
	product_list = get_list_or_404(Product, id__in = id_list)
	print(product_list)
	context = {'product_list':product_list}
	return render(request, 'admin/payment_app/create_sku.html',context)


def create_sku_form(request, product_id):
	# to be able to perform an sku creation, we need to provide our secret key to stripe
	stripe.api_key = settings.STRIPE_SECRET_KEY

	# retrieving the corresponding product
	a_product = get_object_or_404(Product, id = product_id)

	# need of all attribute keys to automatically parse the request.POST
	attribute_keys = json.loads(a_product.attribute_dict).keys()
	chosen_attributes = dict()
	for a_key in attribute_keys:
		chosen_attributes[a_key] = request.POST[a_key]

	# passing the number of sku we add, and if it is finite... 
	inventory_dict ={'type':'finite', 'quantity':request.POST['quantity']}

	# trying first to find a sku with same attributes
	SKU = stripe.SKU.list(product = a_product.stripe_identifier)
	print(SKU)
	for a_sku in SKU:
		if a_sku.attributes == chosen_attributes:
			a_sku.inventory['quantity'] =str( int(a_sku.inventory['quantity'])+ int(request.POST['quantity']))
			a_sku.save()
			return redirect(request.META['HTTP_REFERER'])

	# if there is not an already existing sku with this attributes, we create one. 
	stripe.SKU.create( product = a_product.stripe_identifier, attributes= chosen_attributes, price= a_product.price,currency = settings.CURRENCY, inventory = inventory_dict)
	return redirect(request.META['HTTP_REFERER'])

def display_sku(request, ids):
	# needed to retrieve products from stripe
	stripe.api_key= settings.STRIPE_SECRET_KEY

	# needed to retrieve products and their skus from stripe
	id_list = [int(pk) for pk in ids.split(',')]
	product_list = get_list_or_404(Product, id__in = id_list)

	tuple_list = list()
	for a_product in product_list:
		sku_list = list()
		try:
			stripe_product = stripe.Product.retrieve(a_product.stripe_identifier)
			sku_list = stripe_product.skus['data']
			tuple_list.append((a_product, sku_list))
		except:
			tuple_list.append((a_product, []))
	print(tuple_list)
	return render(request,'admin/payment_app/display_sku.html', {'tuple_list': tuple_list})
		
def lower_sku_quantity(request, sku_id ):
	# needed to retrieve the skus
	stripe.api_key=settings.STRIPE_SECRET_KEY
	a_sku = stripe.SKU.retrieve(sku_id)
	if int( a_sku.inventory['quantity']) > int(request.POST['quantity']):
		a_sku.inventory['quantity'] =str( int(a_sku.inventory['quantity'])+ int(request.POST['quantity']))
	else:
		a_sku.inventory['quantity'] = '0'
	a_sku.save()
	return redirect(request.META['HTTP_REFERER'])
	
def delete_sku(request, sku_id):
	# needed to retrieve the skus
	stripe.api_key=settings.STRIPE_SECRET_KEY
	a_sku = stripe.SKU.retrieve(sku_id)
	a_sku.delete()
	return redirect(request.META['HTTP_REFERER'])


def delete_product(request, product_id):
	# needed to retrieve the product
	stripe.api_key=settings.STRIPE_SECRET_KEY
	a_product = get_object_or_404(Product, id = product_id)
	stripe_product = stripe.Product.retrieve(a_product.stripe_identifier)
	for sku in stripe_product.skus['data']:
		sku.delete()
	stripe_product.delete()
	return redirect(request.META['HTTP_REFERER'])


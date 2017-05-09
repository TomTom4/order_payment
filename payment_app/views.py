from django.shortcuts import render,redirect, get_list_or_404, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import stripe
from order_payment import settings
from .models import *
# Create your views here.

# need to be tested
def query_all_unordered_purchases(user):
	return get_list_or_404(Purchase, purchaser=user, order_identifier__isnull =True)

# safe: depend on above
def store(request):
	# user = request.user
	user = User.objects.get(pk=1)
	product_list = get_list_or_404(Product, id__gte=1)
	try:
		purchased_list = query_all_unordered_purchases(user)
	except:
		purchased_list = None
	context = {'product_list':product_list,'purchased_list':purchased_list}
	return render(request,'payment_app/store.html', context)

# need to be tested
def build_my_profile_context(order_list):
	tuple_list = list()
	for an_order in order_list:
		stripe_order = stripe.Order.retrieve(an_order.stripe_identifier)
		tuple_list.append((an_order, stripe_order, list(an_order.purchases.all())))
	return {'tuple_list':tuple_list}

# safe depend on the above 
def my_profile(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY
	# user = request.user
	user = User.objects.get(pk=1)
	order_list = get_list_or_404(Order, purchases__in= get_list_or_404(Purchase, purchaser= user))
	context = build_my_profile_context(order_list)
	return render(request, 'payment_app/my_profile.html', context)
		
# safe
def merchandise_details(request,product_id):
	stripe.api_key = settings.STRIPE_SECRET_KEY
	product = get_object_or_404(Product, id = product_id)
	stripe_product = stripe.Product.retrieve(product.stripe_identifier)
	sku_list = stripe_product.skus.data
	context = {'product': product, 'sku_list': sku_list}
	return render(request, 'payment_app/merchandise_details.html',context)


# need to be refactored and tested
def purchase(request, product_id):
	# user = request.user
	# Dirty work should use the above instead ! ####################################################
	user = User.objects.get(pk=1)
	# *********************************************************************************************

	related_product = get_object_or_404(Product, id=product_id)

	a_dict = dict()
	for a_key in related_product.get_attribute_dict_keys():
		a_dict[a_key] = request.POST[a_key] 

	try:
		purchase_list = get_list_or_404(Purchase, purchaser= user, order_identifier__isnull = True, product= related_product)
		for a_related_purchase in purchase_list:
			if a_related_purchase.get_attribut_dict() == a_dict:
				a_purchase = a_related_purchase
				break
		a_purchase.quantity += int(request.POST['quantity'])
	except:
		a_purchase = Purchase(purchaser=user, product=related_product, quantity=request.POST['quantity'])
		a_purchase.set_attribut_dict(a_dict)

	a_purchase.save()
	return redirect('store')


# safe: depend on above
def cancel_all_purchases(request):
	# user = request.user
	user = User.objects.get(pk=1)
	purchase_list = query_all_unordered_purchases(user)
	for a_purchase in purchase_list:
		a_purchase.delete()
	return redirect('store')

# safe: depend on above
def cancel_purchase(request, purchase_id):
	# user = request.user
	user = User.objects.get(pk=1)
	purchase = get_object_or_404(Purchase, pk = purchase_id)
	purchase.delete()
	return redirect('store')

# safe: tested
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

# need to be tested
def update_purchase(purchase_list, order):
	for a_purchase in purchase_list:
		a_purchase.order_identifier = order
		a_purchase.save()
		print(a_purchase.order_identifier)


# safe
def order(request):
	return render(request,'payment_app/make_order.html')

# safe: depend on above
# need to be refactored
def create_order(request):
	#user = request.user
	user = User.objects.get(pk='1')
	print(user)	
	stripe.api_key = settings.STRIPE_SECRET_KEY

	purchase_list = query_all_unordered_purchases(user)
	order = stripe.Order.create(currency = settings.CURRENCY,
				email = request.POST['email'] ,
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
	modelOrder = Order(stripe_identifier=order.id , total_price = order.amount)
	modelOrder.save()
	update_purchase(purchase_list, modelOrder)
	context= {'modelOrder':modelOrder, 'order':order, 'purchase_list':purchase_list, 'publishable_key': settings.STRIPE_PUBLISHABLE_KEY, 'description':"bucket" }
	return render(request, 'payment_app/pay_page.html', context)

# safe
def payment(request, order_id):
	# user = request.user
	user = User.objects.get(pk=1)
	modelOrder = get_object_or_404(Order, pk=order_id)
	stripe.api_key = settings.STRIPE_SECRET_KEY
	order = stripe.Order.retrieve(modelOrder.stripe_identifier)
	order.pay(source = request.POST['stripeToken'])
	return redirect('store')

# need to be tested
def parse_csv_into_list(data):
	return [int(el) for el in data.split(',')]

# safe :depend on the above 
def create_sku(request, ids):
	id_list = parse_csv_into_list(ids)
	product_list = get_list_or_404(Product, id__in = id_list)
	context = {'product_list':product_list}
	return render(request, 'admin/payment_app/create_sku.html',context)

#need to be tested
# need of all attribute keys to automatically parse the request.POST
def parse_and_retrieve_chosen_attributes(request, product):
	attribute_keys = json.loads(product.attribute_dict).keys()
	chosen_attributes = dict()
	for a_key in attribute_keys:
		chosen_attributes[a_key] = request.POST[a_key]

	return chosen_attributes


# need to be tested
# find a sku accordingly to chosen_attributes and return it. If not , it returns None object	
def find_chosen_sku(sku_list, chosen_attributes):
	chosen_sku = None
	for a_sku in sku_list:
		if a_sku.attributes == chosen_attributes:
			chosent_sku = a_sku
	return chosen_sku


# need to be tested
def update_sku(request, sku):
	a_sku.inventory['quantity'] =str( int(a_sku.inventory['quantity'])+ int(request.POST['quantity']))
	a_sku.save()


# need to be tested
def create_sku_on_stripe(request, product, chosen_attributes):
	# passing the number of sku we add, and if it is finite... 
	inventory_dict ={'type':'finite', 'quantity':request.POST['quantity']}
	try:
		stripe.SKU.create( product = a_product.stripe_identifier, attributes= chosen_attributes, price= a_product.price,currency = settings.CURRENCY, inventory = inventory_dict)
		print('sku successfully created')
	except:# TODO: catch the proper error and handle it
		print("something went wrong")


# safe: depend on the above	
def create_sku_form(request, product_id):
	# to be able to perform a sku creation, we need to provide our secret key to stripe
	stripe.api_key = settings.STRIPE_SECRET_KEY

	# retrieving the corresponding product
	a_product = get_object_or_404(Product, id = product_id)

	# need chosen attributes to create/update the right sku
	chosen_attributes = parse_and_retrieve_chosen_attributes(request, a_product)

	# trying first to find a sku with same attributes
	SKU = stripe.SKU.list(product = a_product.stripe_identifier)
	sku = find_chosen_sku(SKU, chosen_attributes)
	if sku:
		update_sku(request, sku)
		return redirect(request.META['HTTP_REFERER'])
	else:
		# if there is not an already existing sku with this attributes, we create one. 
		create_sku_on_stripe(request, a_product, chosen_attributes)
		return redirect(request.META['HTTP_REFERER'])


# need to be refactored and tested
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

# need to be refactored and tested
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


# safe
def delete_sku(request, sku_id):
	# needed to retrieve the skus
	stripe.api_key=settings.STRIPE_SECRET_KEY
	a_sku = stripe.SKU.retrieve(sku_id)
	a_sku.delete()
	return redirect(request.META['HTTP_REFERER'])

# safe
def delete_product(request, product_id):
	# needed to retrieve the product
	stripe.api_key=settings.STRIPE_SECRET_KEY
	a_product = get_object_or_404(Product, id = product_id)
	stripe_product = stripe.Product.retrieve(a_product.stripe_identifier)
	for sku in stripe_product.skus['data']:
		sku.delete()
	stripe_product.delete()
	return redirect(request.META['HTTP_REFERER'])

#need to be refactored and tested
def handle_order_status(request, ids):
	# needed to retrieve orders from stripe
	stripe.api_key= settings.STRIPE_SECRET_KEY

	# needed to retrieve orders and their skus from stripe
	id_list = [int(pk) for pk in ids.split(',')]
	order_list = get_list_or_404(Order, id__in = id_list)

	tuple_list = list()
	for an_order in order_list:
		username = an_order.purchases.all()[0].purchaser.username
		stripe_order = stripe.Order.retrieve(an_order.stripe_identifier)
		tuple_list.append((an_order, stripe_order, username))

	return render(request, 'admin/payment_app/handle_order_status.html', {'tuple_list':tuple_list})

# safe
def update_order_status(request, order_id):
	order_to_update = get_object_or_404(Order, id = order_id)
	stripe.api_key = settings.STRIPE_SECRET_KEY
	stripe_order= stripe.Order.retrieve(order_to_update.stripe_identifier)
	stripe_order.status = request.POST['status']
	stripe_order.save()
	return redirect(request.META['HTTP_REFERER'])
	

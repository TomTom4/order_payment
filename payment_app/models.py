from django.template.defaulttags import register
from django.db import models
from django.contrib.auth.models import User
import json


# here a class that represent all the  s we are selling
class Product(models.Model):
	name = models.CharField(max_length=55)
	stripe_identifier = models.CharField(max_length=255,blank=True, default=None)
	remaining_items = models.IntegerField()
	description = models.CharField(max_length=255)
	attribute_dict = models.TextField()
	price = models.IntegerField()
	
	def __str__(self):
		return "it's a {0}, and it cost {1}".format(self.description, self.price)

	# had to do this little trick because there is no other way to store a list into a database
	def set_attribute_dict(self, attribute_dict):
		self.attribute_dict = json.dumps(attribute_dict)
		self.save()

	@register.filter
	def get_attribute_list_by_key(self, a_key):
		return json.loads(self.attribute_dict)[a_key]

	@register.filter
	def get_attribute_dict_keys(self):
		return json.loads(self.attribute_dict).keys()
	
	def __str__(self):
		return self.description

class Order(models.Model):
	stripe_identifier = models.CharField(max_length=55)
	total_price = models.IntegerField()# in cents


class Purchase(models.Model):
	order_identifier = models.ForeignKey(Order, related_name='purchases', null=True, default=None)
	purchaser = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='purchase')
	attribut_dict = models.TextField(blank=True)
	
	def set_attribut_dict(self, attribut_dict):
		self.attribut_dict = json.dumps(attribut_dict)

	def get_attribut_dict(self):
		return json.loads(self.attribut_dict)
	def __str__(self):
		if self.order_identifier:
			return "{0} purchased {1}, and payed it on the order n° : {3}".format(self.purchaser, self.product, self.order_identifier)
		else:
			return " {0} purchased {1}".format(self.purchaser, self.product)


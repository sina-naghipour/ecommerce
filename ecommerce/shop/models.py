from django.db import models
import uuid

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name 


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    related_products = models.ForeignKey('self',related_name='products' , on_delete=models.PROTECT, null=True )
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    color = models.CharField(max_length=255, null=True)
    # stock keeping unit
    sku = models.IntegerField()
    def __str__(self):
        return self.name + ' : ' + self.color


class Variant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=255, null=True)
    # stock keeping unit
    sku = models.IntegerField()

    def __str__(self):
        return self.name + ' : ' + self.color


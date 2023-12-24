from django.db import models

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address =  models.CharField(max_length=255)
    my_cart = models.ForeignKey('shop.Product', on_delete=models.PROTECT)


class AnonymousCustomer(models.Model):
    pass


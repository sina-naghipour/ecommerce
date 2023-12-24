from django.db import models
import uuid
class Seller(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    products = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='seller')

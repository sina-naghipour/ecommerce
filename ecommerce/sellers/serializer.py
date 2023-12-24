from rest_framework import serializers
from models import Seller
class SellerSerializer(serializers.Serializer):
    class Meta:
        model = Seller
        fields = ['id','name', 'password']

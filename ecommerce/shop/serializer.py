from rest_framework import serializers
from .models import Product, Variant, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField()
    def get_category_id(self, product):
        return product.category_id
    class Meta:
        model = Product
        fields = '__all__'

class VariantSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    def get_product(self, variant):
        return variant.product_id
    class Meta:
        model = Variant
        fields = '__all__'


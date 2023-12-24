from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, Variant
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .serializer import ProductSerializer
class ProductViewSet(viewsets.ViewSet):

    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer

    def list(self, request, count=None):
        if count == None:
            products = Product.objects.all()
            products = JSONRenderer().render(ProductSerializer(products, many=True).data)
            return Response(products)
        products = Product.objects.all()[:count]
        products = JSONRenderer().render(ProductSerializer(products, many=True).data)
        return Response(products)

    def add(self, request):
        data=dict(request.data)
        for key in data:
            data[key] = data[key][0]
        product = ProductSerializer(data=data)
        print(data)
        if product.is_valid():
            product.save()
            return Response(f'Product {product.name} Added To Your Store')
        else:
            return Response(product.errors, status=status.HTTP_400_BAD_REQUEST)


class VariantViewSet(viewsets.ViewSet):
    pass
 
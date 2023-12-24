from django.urls import path, register_converter
from .classes import IdConverter
from .views import ProductViewSet
register_converter(IdConverter,'id')

urlpatterns = [

    path('product/view/<int:count>',ProductViewSet.as_view({'get': 'list'}), name='product-view'),
    path('product/add/',ProductViewSet.as_view({'post' : 'add'}), name='product-add'),
    # path('product/<id:id>/change/',ChangeProduct.as_view(), name='product-change'),
    # path('product/<id:id>/delete/',DeleteProduct.as_view(), name='product-delete'),

    # path('variant/<id:id>/view/',ViewVariant.as_view(), name='variant-view'),
    # path('variant/<id:id>/add/',AddVariant.as_view(), name='variant-add'),
    # path('variant/<id:id>/change/',ChangeVariant.as_view(), name='variant-change'),
    # path('variant/<id:id>/delete/',DeleteVariant.as_view(), name='variant-delete'),

]

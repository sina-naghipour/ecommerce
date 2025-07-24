from django.urls import path
from products.views import ProductsAdd, ProductsInventory, ProductsList, ProductsEdit, ProductsDelete


app_name = 'products'


urlpatterns = [
    path('', ProductsList.as_view(), name='products_list'),
    path('add/', ProductsAdd.as_view(), name='products_add'),
    path('edit/<int:pk>/', ProductsEdit.as_view(), name='products_edit'),
    path('delete/<int:pk>/', ProductsDelete.as_view(), name='products_delete'),
    path('inventory/<int:pk>/', ProductsInventory.as_view(), name='inventory'),
]

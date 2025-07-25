from django.urls import path
from orders.views import OrderList, OrderDetail, update_order_status, order_print_view, UserOrdersView

app_name = 'orders'

urlpatterns = [
    path('', OrderList.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetail.as_view(), name='order_detail'),
    path('<int:pk>/print/', order_print_view, name='order_print'),
    path('<int:pk>/update-status/', update_order_status, name='update_status'),
    path('user/<int:pk>/orders/', UserOrdersView.as_view(), name='user_orders'),

]
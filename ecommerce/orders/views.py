from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order
from orders.forms import OrderStatusForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views.decorators.http import require_http_methods
from django.contrib import messages
from accounts.models import CustomUser

class OrderList(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

class OrderDetail(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'

@require_http_methods(["POST"])
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Order.ORDER_STATUS).keys():
        order.status = new_status
        order.save()
        messages.success(request, 'وضعیت سفارش با موفقیت به‌روزرسانی شد.')
        
        if request.headers.get('HX-Request'):
            # Return just the status section for HTMX
            return render(request, 'partials/status_form.html', {'order': order})
        
    else:
        messages.error(request, 'وضعیت انتخاب شده معتبر نیست.')
    
    return redirect('orders:order_detail', pk=order.pk)

def order_print_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/print.html', {
        'order': order
    })


class UserOrdersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/user_orders.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def test_func(self):
        user = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        return self.request.user.is_superuser or self.request.user == user
    
    def get_queryset(self):
        user = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        
        queryset = Order.objects.filter(customer__user=user).order_by('-created_at')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        return context
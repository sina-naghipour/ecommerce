from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, InventoryLog, Category
from .forms import ProductForm, InventoryAdjustmentForm, ProductFilterForm
from django.http import JsonResponse
import uuid
class ProductsList(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('category')
        form = ProductFilterForm(self.request.GET)
        
        if form.is_valid():
            data = form.cleaned_data
            if data.get('q'):
                queryset = queryset.filter(
                    Q(name__icontains=data['q']) | 
                    Q(sku__icontains=data['q']) |
                    Q(description__icontains=data['q'])
                )
            if data.get('category'):
                queryset = queryset.filter(category=data['category'])
            if data.get('status') == 'active':
                queryset = queryset.filter(is_active=True)
            elif data.get('status') == 'draft':
                queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ProductFilterForm(self.request.GET)
        context['categories'] = Category.objects.filter(is_active=True)
        return context

class ProductsAdd(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/add.html'
    success_url = reverse_lazy('products:products_list')
    
    def form_valid(self, form):
        # Set the created_by user
        form.instance.created_by = self.request.user
        
        # Generate SKU if not provided (though our form won't provide it)
        if not form.instance.sku:
            form.instance.sku = self.generate_sku(form.instance)
        
        response = super().form_valid(form)
        messages.success(self.request, 'محصول با موفقیت ایجاد شد.')
        return response
    
    def generate_sku(self, product):
        """Generate a standardized SKU for products"""
        # Get components
        name_code = (product.name[:3] if product.name else 'GEN').upper()
        random_code2 = uuid.uuid4().hex[:6].upper()  # 6-character random string
        
        return f"SKU-{name_code}-{random_code2}"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'افزودن محصول جدید'
        return context

class ProductsEdit(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/add.html'
    success_url = reverse_lazy('products:products_list')
    
    def form_valid(self, form):
        # Handle file upload specifically
        if 'main_image' in self.request.FILES:
            # Delete old image if it exists
            if self.object.main_image:
                self.object.main_image.delete(save=False)
            # Assign new image
            self.object.main_image = self.request.FILES['main_image']
        
        response = super().form_valid(form)
        messages.success(self.request, 'محصول با موفقیت ویرایش شد.')
        return response
    
    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")  # Debugging
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ویرایش محصول'
        context['product'] = self.object
        return context

class ProductsDelete(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('products:products_list')
    
    def get(self, request, *args, **kwargs):
        """
        Override GET to prevent template rendering
        """
        self.object = self.get_object()
        try:
            
            self.object.delete()
            messages.success(request, 'محصول با موفقیت حذف شد.')
            
        except Exception as e:
            messages.error(request, 'محصول با موفقیت حذف نشد.')
        
        return redirect('products:products_list')
    
class ProductsInventory(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/inventory.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory_logs'] = InventoryLog.objects.filter(
            product=self.object
        ).order_by('-created_at')[:50]
        context['form'] = InventoryAdjustmentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = InventoryAdjustmentForm(request.POST)
        
        if form.is_valid():
            adjustment_type = form.cleaned_data['adjustment_type']
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            
            # Calculate new stock
            if adjustment_type == 'set':
                new_stock = quantity
            elif adjustment_type == 'add':
                new_stock = product.stock + quantity
            else:  # subtract
                new_stock = max(0, product.stock - quantity)
            
            # Create inventory log
            InventoryLog.objects.create(
                product=product,
                user=request.user,
                adjustment_type=adjustment_type,
                quantity=quantity,
                previous_stock=product.stock,
                new_stock=new_stock,
                notes=notes
            )
            
            # Update product stock
            product.stock = new_stock
            product.save()
            
            messages.success(request, 'موجودی محصول با موفقیت بروزرسانی شد.')
            return redirect('dashboard:inventory', pk=product.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
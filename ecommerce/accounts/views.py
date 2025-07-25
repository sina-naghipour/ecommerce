from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, ListView, DeleteView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import CustomUser
from accounts.forms import RegisterForm, LoginForm, CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView, RedirectView, CreateView, DeleteView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from orders.models import Order
from customers.models import Address, Customer

class Dashboard(TemplateView):
    template_name = 'dashboard/overview.html'


class Register(CreateView):
    model = CustomUser
    form_class = RegisterForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            # First save the user
            response = super().form_valid(form)
            
            # Get credentials from form
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            
            # Authenticate the user
            user = authenticate(
                request=self.request,
                email=email,
                password=password
            )
            
            if user is None or isinstance(user, AnonymousUser):
                # If authentication fails, log the error but still redirect to success URL
                # You might want to add messages.error() here
                return response
            
            # Login the user
            login(self.request, user)
            return response
            
        except Exception as e:
            # Log the error (you should configure logging in your project)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error during registration: {str(e)}")
            
            # Return the form_invalid response which will show the form with errors
            return self.form_invalid(form)
    
    
class Login(LoginView):
    form_class = LoginForm
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')

class Logout(LogoutView):
    next_page = reverse_lazy('accounts:login')



class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Add any filtering logic here if needed
        return queryset.order_by('-date_joined')

class UserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/detail.html'
    context_object_name = 'user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Add any post-save logic here
        return response

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/user_form.html'
    context_object_name = 'user'
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        context['is_admin'] = self.request.user.is_superuser
        return context
    
    def get_success_url(self):
        return reverse_lazy('accounts:user_detail', kwargs={'pk': self.object.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = kwargs.get('initial', {})
        kwargs['initial']['password'] = ''  # Ensure password field is empty initially
        kwargs['request'] = self.request  # Pass request to form
        return kwargs

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CustomUser
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return self.request.user.is_superuser



class UserToggleStatusView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    pattern_name = 'accounts:user_detail'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=kwargs['pk'])
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(self.request, f"User {status} successfully.")
        return super().get_redirect_url(*args, **kwargs)


class UserAddAddressView(LoginRequiredMixin, CreateView):
    model = Address
    fields = ['title', 'receiver_name', 'phone', 'province', 'city', 'address', 'postal_code', 'is_default']
    template_name = 'users/add_address.html'
    
    def form_valid(self, form):
        form.instance.customer = get_object_or_404(Customer, pk=self.kwargs['user_id'])
        # If setting as default, make sure no other address is default
        if form.cleaned_data.get('is_default'):
            Address.objects.filter(customer=form.instance.customer).update(is_default=False)
        response = super().form_valid(form)
        messages.success(self.request, "آدرس با موفقیت اضافه شد.")
        return response
    
    def get_success_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.kwargs['user_id']})

class UserEditAddressView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Address
    fields = ['title', 'receiver_name', 'phone', 'province', 'city', 'address', 'postal_code', 'is_default']
    template_name = 'users/edit_address.html'
    
    def test_func(self):
        address = self.get_object()
        return self.request.user.is_superuser or self.request.user == address.customer.user
    
    def form_valid(self, form):
        # If setting as default, make sure no other address is default
        if form.cleaned_data.get('is_default'):
            Address.objects.filter(customer=form.instance.customer).exclude(pk=form.instance.pk).update(is_default=False)
        response = super().form_valid(form)
        messages.success(self.request, "آدرس با موفقیت ویرایش شد.")
        return response
    
    def get_success_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.object.customer.pk})

class UserDeleteAddressView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Address
    template_name = 'users/delete_address.html'
    
    def test_func(self):
        address = self.get_object()
        return self.request.user.is_superuser or self.request.user == address.customer.user
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "آدرس با موفقیت حذف شد.")
        return response
    
    def get_success_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.object.customer.pk})

class UserSetDefaultAddressView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    pattern_name = 'accounts:user_detail'
    
    def test_func(self):
        address = get_object_or_404(Address, pk=self.kwargs['pk'])
        return self.request.user.is_superuser or self.request.user == address.customer.user
    
    def get_redirect_url(self, *args, **kwargs):
        address = get_object_or_404(Address, pk=kwargs['pk'])
        # Set all addresses of this customer as non-default first
        Address.objects.filter(customer=address.customer).update(is_default=False)
        # Then set this one as default
        address.is_default = True
        address.save()
        messages.success(self.request, "آدرس پیش‌فرض با موفقیت تنظیم شد.")
        return reverse('accounts:user_detail', kwargs={'pk': address.customer.pk})


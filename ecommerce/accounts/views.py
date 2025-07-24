from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import CustomUser
from accounts.forms import RegisterForm, LoginForm
from django.contrib.auth.models import AnonymousUser

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


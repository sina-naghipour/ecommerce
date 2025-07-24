from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, resolve
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        return self.get_response(request)
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/admin/'):
            return None
            
        try:
            resolved = resolve(request.path)
            url_name = resolved.url_name
            namespace = resolved.namespace
            full_url_name = f"{namespace}:{url_name}" if namespace else url_name
        except:
            return None
            
        LOGIN_EXEMPT_URLS = [
            'accounts:login',
            'accounts:register',
        ]
        
        # Check if URL is exempt
        if full_url_name in LOGIN_EXEMPT_URLS:
            return None
            
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Handle API requests differently
            if request.path.startswith('/api/'):
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=401
                )
                
            return HttpResponseRedirect(
                f"{reverse('accounts:login')}?next={request.path}"
            )
            
        return None



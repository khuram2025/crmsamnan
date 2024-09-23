# domain_routing_middleware.py
from django.http import Http404
from django.conf import settings
from django.shortcuts import redirect

class DomainRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()

        if 'iptportal.channab.com' in host:
            # Let the request follow the normal path for iptportal.channab.com
            pass
        elif 'channab.com' in host:
            # Redirect to a different app, e.g., homepage for channab.com
            request.path_info = '/home/'
        else:
            raise Http404("Host not allowed")

        response = self.get_response(request)
        return response

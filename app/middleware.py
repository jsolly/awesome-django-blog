from django.http import HttpResponsePermanentRedirect

class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        # Allow localhost, IP addresses, and their subdomains in development
        if host in ('localhost', '127.0.0.1', 'testserver', 'www.localhost'):
            return self.get_response(request)
        # Don't redirect IP addresses (they can't have www subdomains)
        if host.replace('.', '').replace(':', '').isdigit():
            return self.get_response(request)
        # Redirect non-www hosts to www for production domains
        if not host.startswith('www.'):
            return HttpResponsePermanentRedirect(
                f"{request.scheme}://www.{host}{request.get_full_path()}"
            )
        return self.get_response(request) 
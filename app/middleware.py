from django.http import HttpResponsePermanentRedirect

class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        if not host.startswith('www.') and host not in ('localhost', '127.0.0.1', 'testserver'):
            return HttpResponsePermanentRedirect(
                f"{request.scheme}://www.{host}{request.get_full_path()}"
            )
        return self.get_response(request) 
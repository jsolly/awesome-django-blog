import os
import re

from django.http import HttpResponsePermanentRedirect


class ReleaseIdMiddleware:
    """Expose Heroku's build identity, including redirects and error responses."""

    def __init__(self, get_response):
        self.get_response = get_response
        commit = os.environ.get("HEROKU_BUILD_COMMIT", "")
        # Local or unconfigured runtimes must never look like a verified release.
        self.release_id = commit if re.fullmatch(r"[0-9a-f]{40}", commit) else "dev"

    def __call__(self, request):
        response = self.get_response(request)
        response["x-release-id"] = self.release_id
        return response


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

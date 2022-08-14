from .utils import add_visitor_if_not_exist
from django.conf import settings

def requestTrackMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if settings.SETTINGS_MODULE == 'django_project.settings.prod':
            add_visitor_if_not_exist(request)
        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware

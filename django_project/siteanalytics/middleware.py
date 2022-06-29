from .utils import add_ip_person_if_not_exist
import os


def requestTrackMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if os.environ["DEBUG"] == "False": #TODO remove when test fixtures comes
            add_ip_person_if_not_exist(request)
        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware

from django.shortcuts import redirect


def handle_no_permission(request, slug):
    """
    Handles the case when the user is not logged in and tries to access the view.
    Redirects the user to the login page, and after successful login, redirects
    back to the original page with the appropriate slug to submit the comment.
    """
    login_url = f"/login/?next=/post/{slug}/" + "#comments-section"

    if not request.user.is_authenticated:
        return redirect(login_url)

    # If the user is logged in, redirect to the original page to submit the comment
    return redirect("post-detail", slug=slug)

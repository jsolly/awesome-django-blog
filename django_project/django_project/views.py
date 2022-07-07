from django.shortcuts import render
from siteanalytics.models import Visitor


def handler_404(request, exception):
    return render(request, "blog/404_page.html")


def works_cited_view(request):
    return render(
        request,
        "blog/works_cited.html",
    )


def security_txt_view(request):
    return render(
        request,
        "blog/security.txt",
    )


def security_pgp_key_view(request):
    return render(
        request,
        "blog/pgp-key.txt",
    )


def portfolio_view(request):
    return render(request, "blog/portfolio.html", {"visitors": Visitor.objects.all()})

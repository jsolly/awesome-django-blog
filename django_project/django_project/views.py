from django.shortcuts import render


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

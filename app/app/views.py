from django.shortcuts import render

def handler_404(request, exception):
    return render(request, "404.html", status=404)

def works_cited_view(request):
    return render(
        request,
        context={
            "title": "Works Cited | Blogthedata.com",
            "description": "Curated list of inspirations & resources from a geospatial software engineer. Get insights on the latest techniques & create a successful blog.",
        },
        template_name="blog/works_cited.html",
    )


def privacy_view(request):
    return render(
        request,
        context={
            "title": "Privacy Policy | Blogthedata.com",
            "description": "I don't collect any information about you. I'm just a guy who likes to blog. You can read my privacy policy here.",
        },
        template_name="blog/privacy.html",
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

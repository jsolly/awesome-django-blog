import aiohttp
import asyncio
import ssl
from django.shortcuts import render, get_object_or_404

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

def road_map_view(request):
    from django_project.settings import GIT_TOKEN
    from datetime import date

    # project_url = "https://api.github.com/projects/14278916"
    in_progress_column_url = "https://api.github.com/projects/columns/18242400"
    backlog_column_url = "https://api.github.com/projects/columns/18271705"
    next_sprint_column_url = "https://api.github.com/projects/columns/18739295"
    HEADERS = {"Authorization": f"token {GIT_TOKEN}"}

    async def make_request(session, url, params=None):
        async with session.get(url, params=params, ssl=ssl.SSLContext()) as resp:
            return await resp.json()

    async def main(urls):
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            tasks = []
            for url in urls:
                tasks.append(asyncio.ensure_future(make_request(session, url)))

            tasks.append(
                asyncio.ensure_future(
                    make_request(
                        session,
                        url="https://api.github.com/repos/jsolly/blogthedata/issues",
                        params={"state": "open"},
                    )
                )
            )

            return await asyncio.gather(*tasks)

    urls = [
        f"{in_progress_column_url}/cards",
        f"{backlog_column_url}/cards",
        f"{next_sprint_column_url}/cards",
    ]

    inprog_cards, backlog_cards, next_sprint_cards, all_open_issues = asyncio.run(
        main(urls)
    )

    inprog_issue_urls = [card["content_url"] for card in inprog_cards]
    backlog_issue_urls = [card["content_url"] for card in backlog_cards]
    next_sprint_issue_urls = [card["content_url"] for card in next_sprint_cards]

    inprog_issues = [
        issue for issue in all_open_issues if issue["url"] in inprog_issue_urls
    ]
    backlog_issues = [
        issue for issue in all_open_issues if issue["url"] in backlog_issue_urls
    ]
    next_sprint_issues = [
        issue for issue in all_open_issues if issue["url"] in next_sprint_issue_urls
    ]

    sprint_number = date.today().isocalendar()[1] // 2  # Two week sprints
    return render(
        request,
        "blog/roadmap.html",
        {
            "all_open_issues": all_open_issues,
            "backlog_issues": backlog_issues,
            "inprog_issues": inprog_issues,
            "next_sprint_issues": next_sprint_issues,
            "sprint_number": sprint_number,
        },
    )

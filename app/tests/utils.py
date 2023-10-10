from users.models import User
from blog.models import Post, Category
from django.db import transaction
from django.contrib.messages import get_messages

# Global counter variable
post_counter = 0


def message_in_response(response, message: str):
    for resp_message in get_messages(response.wsgi_request):
        if message == resp_message.message:
            return True
    return False


@transaction.atomic  # This decorator ensures the function runs in a single database transaction
def create_unique_post(
    author="admin",
    category="uncategorized",
    title_base="Test Post",
    slug_base="test-post",
    metadesc="Default Meta Description",
    draft=False,
    snippet="Default Snippet",
    content="Default Content",
):
    global post_counter  # Declare the global variable

    # Increment the counter value
    post_counter += 1

    title = f"{title_base} {post_counter}"
    slug = f"{slug_base}-{post_counter}"

    author = User.objects.get(username=author)
    category = Category.objects.get(slug=category)

    post = Post.objects.create(
        title=title,
        slug=slug,
        category=category,
        metadesc=metadesc,
        draft=draft,
        snippet=snippet,
        content=content,
        author=author,
    )

    return post


def create_comment(post, author="admin", content="Lorem Ipsum"):
    author = User.objects.get(username=author)
    return post.comments.create(author=author, content=content)


def create_several_unqiue_posts(number_of_posts):
    for _ in range(number_of_posts):
        create_unique_post()

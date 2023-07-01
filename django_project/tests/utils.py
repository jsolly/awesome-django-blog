from users.models import User
from blog.models import Post, Category
from django.contrib.messages import get_messages

# keep track of how many users and posts have been created
user_count = 0
post_count = 0


def message_in_response(response, message: str):
    for resp_message in get_messages(response.wsgi_request):
        if message == resp_message.message:
            return True
    return False


def create_user(super_user=False):
    global user_count  # This allows the function to modify 'user_count'
    username = f"user{user_count}"
    email = f"user{user_count}@test.com"
    password = "defaultpassword"

    user = User(username=username, email=email)
    user.set_password(password)
    if super_user:
        user.is_staff = True
        user.is_superuser = True

    user.save()
    user_count += 1  # Increment the count

    return User.objects.get(username=username)


def create_post(
    author=None,
    category=None,
    title=None,
    slug=None,
    metadesc="Default Meta Description",
    draft=False,
    snippet="Default Snippet",
    content="Default Content",
):
    global post_count
    if not author:
        author = create_user()
    if not category:
        category = Category.objects.get(name="Test Category")
    if not title:
        title = f"Default Title {post_count}"
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
    post_count += 1
    return post


def create_comment(post, author=None, content="Lorem Ipsum"):
    if not author:
        author = create_user()
    return post.comments.create(author=author, content=content)


def create_several_posts(number_of_posts):
    for _ in range(number_of_posts):
        create_post()

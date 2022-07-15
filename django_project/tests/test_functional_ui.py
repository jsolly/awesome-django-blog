from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

# import geckodriver_autoinstaller
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django import setup
from django.urls import reverse
import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()
from users.models import User
from blog.models import Category, Post

# from unittest import skip

# geckodriver_autoinstaller.install()
import ssl

if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
    ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = ssl._create_unverified_context
chromedriver_autoinstaller.install()


# @skip("Tests take too long to run")
class TestFunctionalUI(StaticLiveServerTestCase):
    def setUp(self):
        self.general_password = "T3stingIsFun!"

        def create_user(provided_username, super_user=False):
            try:
                return User.objects.get(username=provided_username)

            except User.DoesNotExist:
                self.provided_username = User(
                    username=provided_username, email="test@original.com"
                )
                self.provided_username.set_password(self.general_password)
                if super_user:
                    self.provided_username.is_staff = True
                    self.provided_username.is_superuser = True

                self.provided_username.save()
                return User.objects.get(username=provided_username)

        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)

        self.super_user = create_user("John_Solly", super_user=True)
        self.basic_user = create_user("basic_user", super_user=False)

        # Productivity Category
        try:
            self.productivity_category = Category.objects.get(name="Productivity")
        except Category.DoesNotExist:
            self.productivity_category = Category.objects.create(name="Productivity")

        # regular post
        try:
            self.post1 = Post.objects.get(slug="first-post")
        except Post.DoesNotExist:
            self.post1 = Post.objects.create(
                title="My First Post",
                slug="first-post",
                category=self.productivity_category,
                metadesc="Curious about your health? Look no further!",
                draft=False,
                # metaimg = ""
                # metaimg_mimetype = ""
                snippet="Long ago, the four nations lived together in harmony.",
                content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
                # date_posted = ""
                author=self.super_user,
            )

        # URLs
        self.blog_home = self.live_server_url + reverse("blog-home")
        self.login_url = self.live_server_url + reverse("login")
        self.post1_url = self.live_server_url + reverse(
            "post-detail", args=[self.post1.slug]
        )

    def tearDown(self):
        self.browser.close()

    def do_login(self, username):
        self.browser.get(self.login_url)
        self.browser.find_element(by=By.NAME, value="username").send_keys(username)
        self.browser.find_element(by=By.NAME, value="password").send_keys(
            self.general_password
        )
        self.browser.find_element(By.ID, value="main-login-button").click()

    def test_author_post_crud(self):
        self.do_login(self.super_user.username)

        # Author clicks on the 'New Post' nav option
        self.browser.find_element(By.ID, value="nav-new-post").click()

        # Author Enters required fields
        self.browser.find_element(by=By.NAME, value="title").send_keys(
            "Super User's Post"
        )
        self.browser.find_element(by=By.NAME, value="slug").send_keys("super-user-post")
        Select(
            self.browser.find_element(by=By.NAME, value="category")
        ).select_by_visible_text("Productivity")
        actions = ActionChains(self.browser)
        actions.send_keys(Keys.TAB * 4).perform()
        actions.send_keys("Some Content").perform()

        # Author scrolls down and clicks 'Create Post'
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        post_create_button = self.browser.find_element(
            By.ID, value="post-create-button"
        )
        actions.move_to_element(post_create_button).click().perform()

        # Author is brought to Post details page
        self.assertEqual(
            self.browser.find_element(by=By.TAG_NAME, value="h2").text,
            "Super User's Post",
        )

        # Author visits Blog Home to see that the post is the first one on the page
        self.browser.find_element(By.ID, value="post-back-to-home-button").click()
        first_post = self.browser.find_element(by=By.CLASS_NAME, value="article-block")
        # Author checks the first article to make sure the created post is there

        self.assertTrue("Super User's Post" in first_post.text)
        # Author clicks on the post's title to get to its post details page
        first_post.click()

        # Author Clicks 'Edit Post' and changes the post's title
        self.browser.find_element(By.ID, value="post-edit-button").click()
        self.browser.find_element(by=By.NAME, value="title").send_keys("Edit ")

        # Author scrolls down and clicks 'Create Post'
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        self.browser.find_element(By.ID, value="post-update-button").click()

        # Author is brought to the post details page and the title is updated
        self.assertEqual(
            self.browser.find_element(by=By.TAG_NAME, value="h2").text,
            "Edit Super User's Post",
        )

        # Author clicks "Delete Post"
        self.browser.find_element(By.ID, value="post-delete-button").click()

        # Author confirms deletion
        self.browser.find_element(By.ID, value="confirm-delete-button").click()

        # Author is brought to blog Home and the post is not present
        first_post = self.browser.find_element(by=By.CLASS_NAME, value="article-block")
        self.assertFalse("Super User's Post" in first_post.text)

    # def test_anonymous_can_register_workflow(self):
    #     # User navigates to Home Page
    #     self.browser.get(self.blog_home)

    #     # User clicks on 'register' nav option
    #     self.browser.find_element(By.ID, value="nav-register").click()

    #     # User enters their information
    #     self.browser.find_element(by=By.NAME, value="username").send_keys(
    #         "selenium_user"
    #     )
    #     self.browser.find_element(by=By.NAME, value="first_name").send_keys("Michael")
    #     self.browser.find_element(by=By.NAME, value="last_name").send_keys("Jenkins")
    #     self.browser.find_element(by=By.NAME, value="email").send_keys(
    #         "selenium_user@invalid.com"
    #     )
    #     self.browser.find_element(by=By.NAME, value="password1").send_keys(
    #         self.general_password
    #     )
    #     self.browser.find_element(by=By.NAME, value="password2").send_keys(
    #         self.general_password
    #     )
    #     self.browser.find_element(by=By.NAME, value="secret_password").send_keys(
    #         "African Swallows"
    #     )
    #     self.browser.find_element(by=By.NAME, value="captcha_1").send_keys("PASSED")

    #     # User clicks 'Register' and is now on the sign-in page
    #     self.browser.find_element(By.ID, value="sign-up-button").click()
    #     self.assertEqual(
    #         "Account created for selenium_user",
    #         self.browser.find_element(by=By.CLASS_NAME, value="alert").text,
    #     )

    def test_anonymnous_can_search_for_and_open_a_post(self):
        # Anonymous navigates to Home Page
        self.browser.get(self.blog_home)

        # Anonymous focuses into the search input box and types "Post" and clicks 'Search'
        self.browser.find_element(By.ID, value="search-posts-input").send_keys("Post")
        self.browser.find_element(By.ID, value="search-posts-button").click()

        # At least one post should be shown
        first_post = self.browser.find_element(by=By.CLASS_NAME, value="article-block")

        # Anonymous clicks on post link
        first_post.click()
        self.assertEqual(
            self.browser.find_element(by=By.TAG_NAME, value="h2").text, "My First Post"
        )

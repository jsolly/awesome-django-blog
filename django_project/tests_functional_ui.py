from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
#import geckodriver_autoinstaller
from django import setup
from django.urls import reverse
import os
import time
import random
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()
from users.models import User, Profile
from blog.models import Category, Post

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from django.urls import reverse

# geckodriver_autoinstaller.install() 
chromedriver_autoinstaller.install()

def test_all_links_resolve(self):
    return False
class TestFunctionalUI(StaticLiveServerTestCase):
    def setUp(self):
        self.random_number = random.randint(0,100000)
        self.browser = webdriver.Chrome()

        # Super User
        self.super_user = User(username=f"super_user{self.random_number}", email="super_user@invalid.com")
        self.general_password = "T3stingIsFun!"
        self.super_user.is_staff = True
        self.super_user.is_superuser = True
        self.super_user.set_password(self.general_password)
        self.super_user.save()

        # Basic User
        self.basic_user = User(username=f"basic_user{self.random_number}", email="basic_user@original.com")
        self.general_password = "T3stingIsFun!"
        self.basic_user.is_staff = False
        self.basic_user.is_superuser = False
        self.basic_user.set_password(self.general_password)
        self.basic_user.save()
        self.basic_user_profile = Profile.objects.get(user=self.basic_user)

        # Productivity Category
        self.productivity_category = Category.objects.create(name=f"Productivity{self.random_number}")


        # regular post
        self.post1 = Post.objects.create(
            title="My First Post",
            slug=f"first-post{self.random_number}",
            category=self.productivity_category.name,
            metadesc="Curious about your health? Look no further!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=self.super_user
            # likes
            # views
        )
        # URLs
        self.home_url = self.live_server_url + reverse("blog-home")
        self.login_url = self.live_server_url + reverse("login")
        self.post1_url = self.live_server_url + reverse("post-detail", args=[self.post1.slug])

    def tearDown(self):
        self.browser.close()

    def do_login(self, username):
        self.browser.get(self.login_url)
        self.browser.find_element(by=By.NAME, value="username").send_keys(username)
        self.browser.find_element(by=By.NAME, value="password").send_keys(self.general_password)
        self.browser.find_element(By.ID, value="main-login-button").click()

    def test_author_post_CRUD(self):
        self.do_login(self.super_user.username)

        # Author clicks on the 'New Post' nav option
        self.browser.find_element(By.ID, value='nav-new-post').click()

        # Author Enters required fields
        self.browser.find_element(by=By.NAME, value="title").send_keys("Super User's Post")
        self.browser.find_element(by=By.NAME, value="slug").send_keys(f"super-user-post{self.random_number}")
        Select(self.browser.find_element(by=By.NAME, value="category")).select_by_value("site updates")
        actions = ActionChains(self.browser)
        actions.send_keys(Keys.TAB * 4).perform()
        actions.send_keys("Some Content").perform()
        
        # Author scrolls down and clicks 'Create Post'
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        post_create_button = self.browser.find_element(By.ID, value="post-create-button")
        actions.move_to_element(post_create_button).click().perform()

        # Author is brought to Post details page
        self.assertEqual(self.browser.find_element(by=By.TAG_NAME, value="h2").text, "Super User's Post")

        # Author visits Blog Home to see that the post is the first one on the page
        self.browser.find_element(By.ID, value="post-back-to-home-button").click()
        first_post = self.browser.find_element(by=By.TAG_NAME, value="article")
        # Author checks the first article to make sure the created post is there

        self.assertTrue("Super User's Post" in first_post.text)
        # Author clicks on the post's title to get to its post details page
        first_post.find_element(by=By.TAG_NAME, value="a").click()
        #self.browser.get(first_article_link.get_attribute("href"))
        
        # Author Clicks 'Edit Post' and changes the post's title
        self.browser.find_element(By.ID, value='post-edit-button').click()
        self.browser.find_element(by=By.NAME, value="title").send_keys(" Edit")

        # Author scrolls down and clicks 'Create Post'
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        self.browser.find_element(By.ID, value="post-update-button").click()

        # Author is brought to the post details page and the title is updated
        self.assertEqual(self.browser.find_element(by=By.TAG_NAME, value="h2").text, "Super User's Post Edit")

        # Author clicks "Delete Post"
        self.browser.find_element(By.ID, value='post-delete-button').click()

        # Author confirms deletion
        self.browser.find_element(By.ID, value='confirm-delete-button').click()

        # Author is brought to blog Home and the post is not present
        first_article = self.browser.find_element(by=By.TAG_NAME, value="article")
        self.assertFalse("Super User's Post" in first_article.text)

    def test_anonymous_can_register_workflow(self):
        # User navigates to Home Page
        self.browser.get(self.home_url)
        
        # User clicks on 'register' nav option
        self.browser.find_element(By.ID, value="nav-register").click()

        # User enters their information
        self.browser.find_element(by=By.NAME, value="username").send_keys("selenium_user")
        self.browser.find_element(by=By.NAME, value="email").send_keys("selenium_user@invalid.com")
        self.browser.find_element(by=By.NAME, value="password1").send_keys(self.general_password)
        self.browser.find_element(by=By.NAME, value="password2").send_keys(self.general_password)
        self.browser.find_element(by=By.NAME, value="secret_password").send_keys("African Swallows")
        self.browser.find_element(by=By.NAME, value="captcha_1").send_keys("PASSED")

        # User clicks 'Register' and is now on the sign-in page
        self.browser.find_element(By.ID, value="sign-up-button").click()
        self.assertEqual(self.browser.find_element(by=By.TAG_NAME, value="legend").text, "Login")
        self.assertEqual("Account created for selenium_user", self.browser.find_element(by=By.CLASS_NAME, value="alert").text)

    def test_anonymnous_can_search_for_and_open_a_post(self):
        # Anonymous navigates to Home Page
        self.browser.get(self.home_url)

        # Anonymous focuses into the search input box and types "Post" and clicks 'Search'
        self.browser.find_element(By.ID, value="search-posts-input").send_keys("Post")
        self.browser.find_element(By.ID, value='search-posts-button').click()

        # At least one post should be shown
        first_post = self.browser.find_element(by=By.TAG_NAME, value="article")

        # Anonymous clicks on post link
        first_post.find_element(by=By.TAG_NAME, value="a").click()
        self.assertEqual(self.browser.find_element(by=By.TAG_NAME, value="h2").text, "My First Post")

    

    def test_basic_user_can_comment_on_a_post(self):
        self.do_login(self.basic_user.username)
        self.browser.get(self.post1_url)
        self.browser.find_element(By.ID, value="comment-create-button").click()

        # Productivity page displays
        self.assertEqual(self.browser.find_element(By.TAG_NAME, value="h1").text, f"Add Comment")

    
    def test_anonymmous_can_like_unlike_a_post(self):
        # Anonymous opens a link to a post
        self.browser.get(self.post1_url)
        self.browser.find_element(By.ID, value="post-like-button").click()
        self.browser.find_element(By.ID, value="post-unlike-button")

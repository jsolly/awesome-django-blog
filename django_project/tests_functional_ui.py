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
        self.random_number = random.randint(0,1000)
        self.browser = webdriver.Chrome()
        #self.browser = webdriver.Firefox()
         
        # Basic User
        self.basic_user = User(username=f"basic_user{self.random_number}", email="basic_user@original.com")
        self.general_password = "T3stingIsFun!"
        self.basic_user.is_staff = False
        self.basic_user.is_superuser = False
        self.basic_user.set_password(self.general_password)
        self.basic_user.save()
        self.basic_user_profile = Profile.objects.get(user=self.basic_user)

        # Super User
        self.super_user = User(username=f"super_user{self.random_number}", email="super_user@original.com")
        self.general_password = "T3stingIsFun!"
        self.super_user.is_staff = True
        self.super_user.is_superuser = True
        self.super_user.set_password(self.general_password)
        self.super_user.save()
        self.super_user_profile = Profile.objects.get(user=self.super_user)


        # Productivity Category
        self.productivity_category = Category.objects.create(name=f"Productivity{self.random_number}")

        # draft post
        self.draft_post = Post.objects.create(
            title="Draft Post",
            slug=f"draft-post{self.random_number}",
            category=self.productivity_category.name,
            metadesc="Curious about your health? Look no further!",
            draft=True,
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            author=self.super_user

        )

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
        self.roadmap_url = self.live_server_url + reverse("blog-roadmap")
        self.login_url = self.live_server_url + reverse("login")
        self.post1_url = self.live_server_url + reverse("post-detail", args=[self.post1.slug])

    def tearDown(self):
        self.browser.close()

    def do_login(self, username):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(username)
        self.browser.find_element_by_name("password").send_keys(self.general_password)
        self.browser.find_element_by_id("main-login-button").click()

        

    def test_author_post_CRUD(self):
        self.do_login(self.super_user.username)

        # Author clicks on the 'New Post' nav option
        self.browser.find_element_by_id('nav-new-post').click()


        # Author Enters required fields
        self.browser.find_element_by_name("title").send_keys("Super User's Post")
        self.browser.find_element_by_name("slug").send_keys(f"super-user-post{self.random_number}")
        Select(self.browser.find_element_by_name("category")).select_by_value("site updates")
        actions = ActionChains(self.browser)
        actions.send_keys(Keys.TAB * 4).perform()
        actions.send_keys("Some Content").perform()
        
        # Author scrolls down and clicks 'Create Post'
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        post_create_button = self.browser.find_element_by_id("post-create-button")
        actions.move_to_element(post_create_button).click().perform()

        # Author is brought to Post details page
        self.assertEqual(self.browser.find_element_by_tag_name("h2").text, "Super User's Post")

        # Author visits Blog Home to see that the post is the first one on the page
        self.browser.find_element_by_id("post-back-to-home-button").click()
        first_post = self.browser.find_element_by_tag_name("article")
        # Author checks the first article to make sure the created post is there

        self.assertTrue("Super User's Post" in first_post.text)
        # Author clicks on the post's title to get to its post details page
        first_post.find_element_by_tag_name("a").click()
        #self.browser.get(first_article_link.get_attribute("href"))
        
        # Author Clicks 'Edit Post' and changes the post's title
        self.browser.find_element_by_id('post-edit-button').click()
        self.browser.find_element_by_name("title").send_keys(" Edit")

        # Author scrolls down and clicks 'Create Post'
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        self.browser.find_element_by_id("post-update-button").click()

        # Author is brought to the post details page and the title is updated
        self.assertEqual(self.browser.find_element_by_tag_name("h2").text, "Super User's Post Edit")

        # Author clicks "Delete Post"
        self.browser.find_element_by_id('post-delete-button').click()

        # Author confirms deletion
        self.browser.find_element_by_id('confirm-delete-button').click()

        # Author is brought to blog Home and the post is not present
        first_article = self.browser.find_element_by_tag_name("article")
        self.assertFalse("Super User's Post" in first_article.text)
        

    def test_anonymous_cannot_see_draft_posts(self):
        # Anonymous navigates to Home Page and can't see any draft posts
        self.browser.get(self.home_url)
        articles = self.browser.find_elements_by_tag_name("article")
        for article in articles:
            self.assertFalse("Draft" in article.text)

        # Anonymous focuses into the search input box and types "Draft" and clicks 'Search'
        self.browser.find_element_by_id("search-posts-input").send_keys("Draft")
        self.browser.find_element_by_id('search-posts-button').click()

        # No posts should be shown
        self.assertRaises(exceptions.NoSuchElementException, self.browser.find_element_by_tag_name, "article")

    def test_nav_options_correct_when_anonymous(self):
        # Anonymous navigates to Home Page
        self.browser.get(self.home_url)
        
        # They notice they are not logged in (No Create Post or Logout options in the nav)
        self.assertRaises(exceptions.NoSuchElementException, self.browser.find_element_by_id, "nav-new-post")
        self.assertRaises(exceptions.NoSuchElementException, self.browser.find_element_by_id, "nav-logout")

    def test_basic_user_sees_correct_nav_options(self):
        self.do_login(self.basic_user.username)

        # User should be on the home page and have a 'Profile' and 'Logout' options in the navbar
        # Basic User should not have a 'create post' button
        self.browser.find_element_by_id("nav-logout")
        self.browser.find_element_by_id("nav-profile")
        self.assertRaises(exceptions.NoSuchElementException, self.browser.find_element_by_id, "nav-new-post")


    def test_anonymous_can_register_workflow(self):
        # User navigates to Home Page
        self.browser.get(self.home_url)
        
        # User clicks on 'register' nav option
        self.browser.find_element_by_id("nav-register").click()

        # User enters their information
        self.browser.find_element_by_name("username").send_keys("selenium_user")
        self.browser.find_element_by_name("email").send_keys("selenium_user@invalid.com")
        self.browser.find_element_by_name("password1").send_keys(self.general_password)
        self.browser.find_element_by_name("password2").send_keys(self.general_password)
        self.browser.find_element_by_name("secret_password").send_keys("African Swallows")
        self.browser.find_element_by_name("captcha_1").send_keys("PASSED")

        # User clicks 'Register' and is now on the sign-in page
        self.browser.find_element_by_id("sign-up-button").click()
        self.assertEqual(self.browser.find_element_by_tag_name("legend").text, "Login")
        self.assertEqual("Account created for selenium_user", self.browser.find_element_by_class_name("alert").text)
        

    def test_anonymnous_can_see_and_navigate_categories_using_side_bar(self):
        # Zhe navigates to Home Page
        self.browser.get(self.home_url)

         # Zhe clicks on 'Productivity' to see posts about saving time. The Category becomes active and the category page is shown.
        self.browser.find_element_by_id(f"sidebar-productivity{self.random_number}").click()
        sidebar_category = self.browser.find_element_by_id(f"sidebar-productivity{self.random_number}")
        self.assertTrue("active" in sidebar_category.get_attribute("class"))
        
        # Finally, she clicks on 'Blog Home' to go back to seeing all posts
        self.browser.find_element_by_id('sidebar-blog-home').click()
        self.assertEqual(self.browser.find_element_by_tag_name("h1").text, "All Categories")

    def test_anonymnous_can_search_for_and_open_a_post(self):
        # Anonymous navigates to Home Page
        self.browser.get(self.home_url)

        # Anonymous focuses into the search input box and types "Post" and clicks 'Search'
        self.browser.find_element_by_id("search-posts-input").send_keys("Post")
        self.browser.find_element_by_id('search-posts-button').click()

        # At least one post should be shown
        first_post = self.browser.find_element_by_tag_name("article")

        # Anonymous clicks on post link
        first_post.find_element_by_tag_name("a").click()
        self.assertEqual(self.browser.find_element_by_tag_name("h2").text, "My First Post")


    def test_anonymnous_can_view_a_github_issue(self):
        # Anonymous navigates to Roadmap page
        self.browser.get(self.roadmap_url)
        
        # Anonymous clicks on a Github Issue link and is directed to a GitHub issue
        self.browser.find_element_by_xpath('//a[contains(@href,"github")]').click()
        opened_tab = self.browser.window_handles[1]
        self.browser.switch_to.window(opened_tab)
        self.assertTrue("github" in self.browser.current_url)

    def test_anonymnous_can_view_the_blog_test_coverage(self):
        # Anonymous navigates to Roadmap page
        self.browser.get(self.roadmap_url)
        
        # Anonymous clicks on a Github Issue link and is directed to a GitHub issue
        self.browser.find_element(by=By.LINK_TEXT, value="Unit Test Coverage").click()
        opened_tab = self.browser.window_handles[1]
        self.browser.switch_to.window(opened_tab)
        self.assertTrue("Coverage" in self.browser.find_element_by_tag_name("h1").text)

    # basic user can access their profile and edit it

    def test_super_user_can_edit_profile(self): # TODO add changing profile photo
        original_username = self.super_user.username
        self.do_login(self.super_user.username)
        self.browser.find_element_by_id("nav-profile").click()
        self.browser.find_element_by_name("username").send_keys("_edit")
        self.browser.find_element_by_id("update-profile-button").click()
        self.assertEqual("Your account has been updated", self.browser.find_element_by_class_name("alert").text)
        
        # Super User checks Home page to see if the posts show the name change
        self.browser.get(self.home_url)
        self.assertTrue(f"{original_username}_edit" in self.browser.find_element_by_tag_name("nobr").text)


    def test_anonymous_can_access_about_page(self):
        # John Solly User
        john_solly_user = User(username=f"John_Solly", email="john_Solly@invalid.com")
        self.general_password = "T3stingIsFun!"
        john_solly_user.is_staff = True
        john_solly_user.is_superuser = True
        john_solly_user.set_password(self.general_password)
        john_solly_user.save()
        self.basic_user_profile = Profile.objects.get(user=john_solly_user)

        # Anonymous visits Home Page and then clicks on 'About' in Navbar
        self.browser.get(self.home_url)
        self.browser.find_element_by_id("nav-about").click()

        # About Me page should display
        self.assertEqual(self.browser.find_element_by_tag_name("h1").text, "About Me")
        

    def test_anonymous_can_access_categories_using_nav(self):
        self.browser.get(self.home_url)
        self.browser.find_element_by_id("navbarDropdown").click()

        #Anonymous choses a dropdown category of 'Productivity'
        categories = self.browser.find_element_by_id("nav-categories")
        categories.find_element_by_link_text(f"Productivity{self.random_number}").click()

        # Productivity page displays
        self.assertEqual(self.browser.find_element_by_tag_name("h1").text, f"Productivity{self.random_number}")


    def test_anonymmous_can_like_unlike_a_post(self):
        # Anonymous opens a link to a post
        self.browser.get(self.post1_url)
        self.browser.find_element_by_id("post-like-button").click()
        self.browser.find_element_by_id("post-unlike-button")



    def basic_user_can_comment_on_a_post(self):
        self.do_login(self.basic_user)
        self.browser.get(self.post1_url)
        self.browser.find_element_by_id("comment-create-button").click()

        # Productivity page displays
        self.assertEqual(self.browser.find_element_by_tag_name("h1").text, f"Add Comment")


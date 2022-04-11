from selenium import webdriver
import chromedriver_autoinstaller
from django import setup
from django.urls import reverse
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()
from users.models import User, Profile

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from django.urls import reverse

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path
class TestFunctionalUI(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.login_url = self.live_server_url + reverse("login")
        self.home_url = self.live_server_url + reverse("blog-home")
        self.basic_user_username = "basic_user"

        # Basic User
        self.basic_user = User(username="test_viewer", email="test@original.com")
        self.general_password = "T3stingIsFun!"
        self.basic_user.is_staff = False
        self.basic_user.is_superuser = False
        self.basic_user.set_password(self.general_password)
        self.basic_user.save()
        self.basic_user_profile = Profile.objects.get(user=self.basic_user)

    def tearDown(self):
        self.browser.close()

    def test_author_CRUD(self):
        return False

    def test_anonymous_permissions(self):
        return False

    def test_basic_user_permissions(self):
        # User navigates to Home Page
        self.browser.get(self.home_url)
        # They notice they are not logged in (No Create Post or Logout options in the nav), so they click on 'Login' in the navbar
        self.browser.find_element_by_name("nav-login").click()
        # They enter their username and password and click the Login button
        self.browser.find_element_by_name("username").send_keys(self.basic_user_username)
        self.browser.find_element_by_name("password").send_keys(self.general_password)
        self.browser.find_element_by_name("login").click()
        # User should be on the home page and have a 'Create Post' and 'Logout' options in the navbar
        self.assertEqual(self.browser.current_url, self.home_url)


    def test_register_workflow(self):
        return False

    def test_site_navigation(self):
        return False

    def test_all_links_resolve(self):
        return False
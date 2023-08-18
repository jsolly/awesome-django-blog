# Local application/library specific imports
from .base import SetUp
from blog.forms import PostForm
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .utils import create_user


class TestForms(SetUp):
    def setUp(self):
        self.test_user = create_user(super_user=True)

    def test_post_form_valid_data(self):
        form = PostForm(
            data={
                "title": "Lorem Ipsum Post",
                "slug": "lorem-ipsum-post",
                "category": self.test_category,
                "metadesc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "draft": False,
                "snippet": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "author": self.test_user,
                "metaimg_alt_txt": "Lorem ipsum",
            }
        )

        self.assertTrue(form.is_valid())

    def test_post_form_no_data(self):
        post_form = PostForm(data={})
        self.assertFalse(post_form.is_valid())
        self.assertEqual(len(post_form.errors), 3)

    # Users Forms
    def test_user_register_form_valid_data(self):
        user_form = UserRegisterForm(
            data={
                "username": "test",
                "email": "example@test.com",
                "first_name": "Tester",
                "last_name": "Smith",
                "password1": "Coff33cak3s!",
                "password2": "Coff33cak3s!",
                "secret_password": "African Swallows",
            }
        )
        self.assertTrue(user_form.is_valid())

    def test_user_update_form_valid_data(self):
        form = UserUpdateForm(data={"email": "example@test.com", "username": "test"})

        self.assertTrue(form.is_valid())

    # Might want to add image validation
    def test_profile_update_form_valid_data(self):
        form = ProfileUpdateForm(data={"image": "image1"})
        self.assertTrue(form.is_valid())

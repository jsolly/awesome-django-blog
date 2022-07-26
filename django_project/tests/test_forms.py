from .base import SetUp
from blog.forms import PostForm
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


class TestForms(SetUp):
    def test_post_form_valid_data(self):
        form = PostForm(
            data={
                "title": "My Second Post",
                "slug": "second-post",
                "category": self.category1,
                "metadesc": "I can make you more productive!",
                "draft": False,
                # "metaimg" : ""
                "snippet": "Do the things",
                "content": "Do the things. All the things",
                # date_posted : ""
                "author": self.super_user,
                "metaimg_alt_txt": "Meta Image Alt-Text",
                # "likes"
                # "views"
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
                "captcha_0": "dummy-value",
                "captcha_1": "PASSED",
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

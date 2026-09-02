from django.test import TestCase

from .forms import RegisterForm


class RegisterSecurityTests(TestCase):

    def test_rejects_weak_password(self):

        form = RegisterForm(
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "123456",
                "password_confirm": "123456",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_password_is_hashed(self):

        password = "StrongPassword123!"

        form = RegisterForm(
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": password,
                "password_confirm": password,
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save(commit=False)
        user.set_password(
            form.cleaned_data["password"]
        )
        user.save()

        self.assertNotEqual(
            user.password,
            password
        )

        self.assertTrue(
            user.check_password(password)
        )
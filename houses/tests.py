from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .forms import HouseForm


class HouseUploadSecurityTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPassword123!"
        )

    def test_rejects_image_larger_than_5mb(self):
        large_image = SimpleUploadedFile(
            "large.jpg",
            b"0" * (5 * 1024 * 1024 + 1),
            content_type="image/jpeg"
        )

        form = HouseForm(
            data={
                "title": "Test House",
                "description": "Test description",
                "location": "Portugal",
                "price": "100",
                "bedrooms": 2,
                "bathrooms": 1,
                "guests": 4,
            },
            files={
                "image": large_image,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_rejects_more_than_10_additional_images(self):
        images = []

        for i in range(11):
            image = SimpleUploadedFile(
                f"image_{i}.jpg",
                b"fake-image-content",
                content_type="image/jpeg"
            )
            images.append(image)

        form = HouseForm(
            data={
                "title": "Test House",
                "description": "Test description",
                "location": "Portugal",
                "price": "100",
                "bedrooms": 2,
                "bathrooms": 1,
                "guests": 4,
            },
            files={
                "image": SimpleUploadedFile(
                    "main.jpg",
                    b"fake-image-content",
                    content_type="image/jpeg"
                ),
                "additional_images": images,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("additional_images", form.errors)

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_house_create_rejects_request_without_csrf(self):

        self.client = self.client_class(enforce_csrf_checks=True)
        self.client.defaults["wsgi.url_scheme"] = "https"

        self.client.login(
            username="testuser",
            password="StrongPassword123!"
        )

        response = self.client.post(
            "/houses/create/",
            {
                "title": "Malicious House",
                "description": "Test",
                "location": "Portugal",
                "price": "100",
                "bedrooms": 2,
                "bathrooms": 1,
                "guests": 4,
            }
        )

        self.assertEqual(response.status_code, 403)
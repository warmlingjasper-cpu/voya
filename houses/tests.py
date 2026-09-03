from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .forms import HouseForm, ReservationForm
from .models import House, Reservation


class HouseUploadSecurityTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPassword123!"
        )

class ReservationSecurityTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="guest",
            password="StrongPassword123!"
        )

        self.house = House.objects.create(
            owner=self.user,
            title="Test House",
            description="Test description",
            location="Portugal",
            price=100,
            bedrooms=2,
            bathrooms=1,
            guests=4,
            rating=5,
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

    def test_rejects_too_many_guests(self):
        form = ReservationForm(
            data={
                "check_in": "2026-10-10",
                "check_out": "2026-10-12",
                "guests": 999,
            },
            house=self.house,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "__all__",
            form.errors
        )

    def test_rejects_zero_guests(self):
        form = ReservationForm(
            data={
                "check_in": "2026-10-10",
                "check_out": "2026-10-12",
                "guests": 0,
            },
            house=self.house,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "__all__",
            form.errors
        )

    def test_rejects_checkout_before_checkin(self):
        form = ReservationForm(
            data={
                "check_in": "2026-10-12",
                "check_out": "2026-10-10",
                "guests": 2,
            },
            house=self.house,
        )

        self.assertFalse(form.is_valid())

    def test_accepts_valid_reservation(self):
        form = ReservationForm(
            data={
                "check_in": "2026-10-10",
                "check_out": "2026-10-12",
                "guests": 2,
            },
            house=self.house,
        )

        self.assertTrue(form.is_valid())

    def test_rejects_overlapping_reservation(self):
        Reservation.objects.create(
            house=self.house,
            guest=self.user,
            check_in="2026-10-10",
            check_out="2026-10-15",
            guests=2,
            status=Reservation.Status.CONFIRMED,
        )

        overlapping_reservation = Reservation.objects.filter(
            house=self.house,
            status=Reservation.Status.CONFIRMED,
            check_in__lt="2026-10-14",
            check_out__gt="2026-10-12",
        ).exists()

        self.assertTrue(overlapping_reservation)
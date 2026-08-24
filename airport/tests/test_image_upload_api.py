import os
import tempfile

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Airplane
from airport.tests.test_samples import (
    sample_airport,
    sample_city,
    sample_country,
    base_sample_airplane,
    sample_airplane_type,
)


AIRPORT_URL = reverse("airport:airport-list")
AIRPLANE_URL = reverse("airport:airplane-list")


def airport_detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])


def airplane_detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


def airport_image_upload_url(airport_id):
    return reverse("airport:airport-upload-airport-image", args=[airport_id])


def airplane_image_upload_url(airplane_id):
    return reverse("airport:airplane-upload-airplane-image", args=[airplane_id])


class AirportImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@airport.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

        self.airport = sample_airport()

    def tearDown(self):
        if self.airport.image:
            self.airport.image.delete()

    def test_upload_image_to_airport(self):
        url = airport_image_upload_url(self.airport.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(
                url,
                {"image": ntf},
                format="multipart",
            )

        self.airport.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airport.image.path))

    def test_upload_image_bad_request(self):
        url = airport_image_upload_url(self.airport.id)

        res = self.client.post(
            url,
            {"image": "not image"},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airport_list(self):
        city = sample_city(
            name="ImageCity",
            country=sample_country(name="ImageCountry"),
        )

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(
                AIRPORT_URL,
                {
                    "name": "Airport With Image",
                    "closest_big_city": city.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        airport = Airport.objects.get(name="Airport With Image")
        self.assertFalse(airport.image)

    def test_image_url_is_shown_on_airport_detail(self):
        url = airport_image_upload_url(self.airport.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            self.client.post(
                url,
                {"image": ntf},
                format="multipart",
            )

        res = self.client.get(airport_detail_url(self.airport.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airport_list(self):
        url = airport_image_upload_url(self.airport.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            self.client.post(
                url,
                {"image": ntf},
                format="multipart",
            )

        res = self.client.get(AIRPORT_URL)

        self.assertIn("image", res.data["results"][0].keys())


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@airplane.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

        self.airplane = base_sample_airplane()

    def tearDown(self):
        if self.airplane.image:
            self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        url = airplane_image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(
                url,
                {"image": ntf},
                format="multipart",
            )

        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        url = airplane_image_upload_url(self.airplane.id)

        res = self.client.post(
            url,
            {"image": "not image"},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list(self):
        airplane_type = sample_airplane_type(name="ImageAirplaneType")

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(
                AIRPLANE_URL,
                {
                    "name": "Airplane With Image",
                    "rows": 70,
                    "seats_in_row": 6,
                    "airplane_type": airplane_type.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        airplane = Airplane.objects.get(name="Airplane With Image")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = airplane_image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            self.client.post(
                url,
                {"image": ntf},
                format="multipart",
            )

        res = self.client.get(airplane_detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = airplane_image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            self.client.post(
                url,
                {"image": ntf},
                format="multipart",
            )

        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data["results"][0].keys())

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Country
from airport.serializers import CountrySerializer
from airport.tests.test_samples import (
    sample_country,
)


COUNTRY_URL = reverse("airport:country-list")


def detail_url(country_id):
    return reverse("airport:country-detail", args=[country_id])


class UnauthenticatedCountryApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        sample_country()
        res = self.client.get(COUNTRY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCountryApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_country_list(self):

        sample_country()

        res = self.client.get(COUNTRY_URL)

        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_country_create_forbidden(self):

        payload = {
            "name": "TestCountry"
        }

        res = self.client.post(COUNTRY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_country_create(self):
        payload = {
            "name": "TestCountry"
        }

        res = self.client.post(COUNTRY_URL, payload)

        country = Country.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(country, key))

    def test_country_detail_route_not_available(self):
        country = sample_country()

        with self.assertRaises(NoReverseMatch):
            detail_url(country.id)

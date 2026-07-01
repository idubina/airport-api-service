from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import City
from airport.serializers import CityListSerializer
from airport.tests.test_samples import (
    sample_country,
    sample_city
)


CITY_URL = reverse("airport:city-list")


def detail_url(city_id):
    return reverse("airport:city-detail", args=[city_id])


class UnauthenticatedCityApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        sample_city()
        res = self.client.get(CITY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCityApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_city_list(self):

        sample_city()

        res = self.client.get(CITY_URL)

        countries = City.objects.all()
        serializer = CityListSerializer(countries, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_city_filter_by_country_name(self):
        country_1 = sample_country(name="TestCountry1")
        country_2 = sample_country(name="TestCountry2")

        city_1 = sample_city(
            name="TestCity1",
            country=country_1
        )
        city_2 = sample_city(
            name="TestCity2",
            country=country_2
        )

        res = self.client.get(
            CITY_URL,
            {
                "country": f"{country_1.name}"
            }
        )

        serializer_city_1 = CityListSerializer(city_1)
        serializer_city_2 = CityListSerializer(city_2)

        self.assertIn(serializer_city_1.data, res.data["results"])
        self.assertNotIn(serializer_city_2.data, res.data["results"])

    def test_city_create_forbidden(self):

        country = sample_country()

        payload = {
            "name": "TestCity",
            "country": country.id
        }

        res = self.client.post(CITY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCityApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_city_create(self):
        country = sample_country()

        payload = {
            "name": "TestCity",
            "country": country.id
        }

        res = self.client.post(CITY_URL, payload)

        city = City.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "country":
                self.assertEqual(payload[key], getattr(city, "country_id"))
            else:
                self.assertEqual(payload[key], getattr(city, key))

    def test_city_detail_route_not_available(self):
        city = sample_city()

        with self.assertRaises(NoReverseMatch):
            detail_url(city.id)

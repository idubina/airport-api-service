from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import (
    AirportListSerializer,
    AirportRetrieveSerializer,
)
from airport.tests.test_samples import (
    sample_country,
    sample_city,
    sample_airport
)


AIRPORT_URL = reverse("airport:airport-list")


def detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])


class UnauthenticatedAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        sample_airport()
        res = self.client.get(AIRPORT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_airport_list(self):

        sample_airport()

        res = self.client.get(AIRPORT_URL)

        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airport_detail(self):

        airport = sample_airport()

        res = self.client.get(detail_url(airport.id))

        serializer = AirportRetrieveSerializer(airport)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_airport_filter_by_name_or_city(self):
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

        airport_1 = sample_airport(
            name="TestAirport1",
            city=city_1
        )

        airport_2 = sample_airport(
            name="TestAirport2",
            city=city_2
        )

        res_1 = self.client.get(
            AIRPORT_URL,
            {
                "name": f"{airport_1.name}"
            }
        )
        res_2 = self.client.get(
            AIRPORT_URL,
            {
                "city": f"{airport_1.closest_big_city.name}"
            }
        )

        serializer_airport_1 = AirportListSerializer(airport_1)
        serializer_airport_2 = AirportListSerializer(airport_2)

        self.assertIn(serializer_airport_1.data, res_1.data["results"])
        self.assertNotIn(serializer_airport_2.data, res_1.data["results"])
        self.assertIn(serializer_airport_1.data, res_2.data["results"])
        self.assertNotIn(serializer_airport_2.data, res_2.data["results"])

    def test_airport_create_forbidden(self):

        payload = {
            "name": "TestAirport",
            "closest_big_city": sample_city().id
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_airport_create(self):

        payload = {
            "name": "TestAirport",
            "closest_big_city": sample_city().id
        }

        res = self.client.post(AIRPORT_URL, payload)

        airport = Airport.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "closest_big_city":
                self.assertEqual(
                    payload[key],
                    getattr(airport, "closest_big_city_id")
                )
            else:
                self.assertEqual(payload[key], getattr(airport, key))

    def test_airport_delete_not_allowed(self):

        airport = sample_airport()

        res = self.client.delete(detail_url(airport.id))

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_airport_update_not_allowed(self):

        airport = sample_airport()

        payload = {
            "name": "AirportTest2",
            "closest_big_city": sample_city(
                name="TestCity2",
                country=sample_country(name="TestCountry2")
            ).id
        }

        res = self.client.put(detail_url(airport.id), payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

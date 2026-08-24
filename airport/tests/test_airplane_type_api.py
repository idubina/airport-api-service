from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer
from airport.tests.test_samples import (
    sample_airplane_type,
)


AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


def detail_url(airplane_type_id):
    return reverse(
        "airport:airplanetype-detail", args=[airplane_type_id]
    )


class UnauthenticatedAirplaneTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        sample_airplane_type()
        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_airplane_type_list(self):

        sample_airplane_type()

        res = self.client.get(AIRPLANE_TYPE_URL)

        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_airplane_type_filter_by_name(self):
        airplane_type_1 = sample_airplane_type(
            name="TestAirplaneType1"
        )
        airplane_type_2 = sample_airplane_type(
            name="TestAirplaneType2"
        )

        res = self.client.get(
            AIRPLANE_TYPE_URL,
            {
                "name": f"{airplane_type_1.name}"
            }
        )


        serializer_airplane_type_1 = AirplaneTypeSerializer(airplane_type_1)
        serializer_airplane_type_2 = AirplaneTypeSerializer(airplane_type_2)

        self.assertIn(serializer_airplane_type_1.data, res.data["results"])
        self.assertNotIn(serializer_airplane_type_2.data, res.data["results"])

    def test_airplane_type_create_forbidden(self):

        payload = {
            "name": "TestFirstName",
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_airplane_type_create(self):
        payload = {
            "name": "TestFirstName",
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        airplane_type = AirplaneType.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_airplane_type_detail_route_not_available(self):
        airplane_type = sample_airplane_type()

        with self.assertRaises(NoReverseMatch):
            detail_url(airplane_type.id)

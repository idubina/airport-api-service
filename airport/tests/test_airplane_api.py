from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer
)
from airport.tests.test_samples import (
    sample_airplane_1,
    sample_airplane_2,
    base_sample_airplane,
    sample_airplane_type
)


AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id):
    return reverse(
        "airport:airplane-detail", args=[airplane_id]
    )


class UnauthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        base_sample_airplane()
        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_airplane_list(self):

        base_sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airplane_detail(self):

        airplane = base_sample_airplane()

        res = self.client.get(detail_url(airplane.id))

        serializer = AirplaneRetrieveSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_airplane_filter_by_name_or_type(self):
        airplane_1 = sample_airplane_1()
        airplane_2 = sample_airplane_2()

        res_1 = self.client.get(
            AIRPLANE_URL,
            {
                "name": f"{airplane_1.name}"
            }
        )

        res_2 = self.client.get(
            AIRPLANE_URL,
            {
                "airplane_type": f"{airplane_2.airplane_type.name}"
            }
        )


        serializer_airplane_1 = AirplaneListSerializer(airplane_1)
        serializer_airplane_2 = AirplaneListSerializer(airplane_2)

        self.assertIn(serializer_airplane_1.data, res_1.data["results"])
        self.assertNotIn(serializer_airplane_2.data, res_1.data["results"])
        self.assertIn(serializer_airplane_2.data, res_2.data["results"])
        self.assertNotIn(serializer_airplane_1.data, res_2.data["results"])

    def test_airplane_create_forbidden(self):

        payload = {
            "name": "TestAirplane",
            "rows": 70,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_airplane_create(self):
        payload = {
            "name": "TestAirplane",
            "rows": 70,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id
        }

        res = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "airplane_type":
                self.assertEqual(
                    payload[key],
                    getattr(airplane, "airplane_type_id")
                )
            else:
                self.assertEqual(payload[key], getattr(airplane, key))

    def test_airplane_delete_not_allowed(self):

        airplane = base_sample_airplane()

        res = self.client.delete(detail_url(airplane.id))

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_airplane_update_not_allowed(self):

        airplane = base_sample_airplane()

        payload = {
            "name": "TestAirplane2",
            "rows": 70,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type(
                name="TestAirplaneType2",
            ).id
        }

        res = self.client.put(detail_url(airplane.id), payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

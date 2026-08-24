from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewListSerializer
from airport.tests.test_samples import (
    sample_crew,
)


CREW_URL = reverse("airport:crew-list")


def detail_url(crew_id):
    return reverse("airport:crew-detail", args=[crew_id])


class UnauthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        sample_crew()
        res = self.client.get(CREW_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_crew_list(self):

        sample_crew()

        res = self.client.get(CREW_URL)

        crews = Crew.objects.all()
        serializer = CrewListSerializer(crews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_crew_filter_by_first_or_last_name(self):
        crew_1 = sample_crew(
            first_name="TestFirstName1",
            last_name="TestLastName1"
        )
        crew_2 = sample_crew(
            first_name="TestFirstName2",
            last_name="TestLastName2"
        )

        res_1 = self.client.get(
            CREW_URL,
            {
                "first_name": f"{crew_1.first_name}"
            }
        )

        res_2 = self.client.get(
            CREW_URL,
            {
                "last_name": f"{crew_2.last_name}"
            }
        )

        serializer_crew_1 = CrewListSerializer(crew_1)
        serializer_crew_2 = CrewListSerializer(crew_2)

        self.assertIn(serializer_crew_1.data, res_1.data["results"])
        self.assertNotIn(serializer_crew_2.data, res_1.data["results"])
        self.assertIn(serializer_crew_2.data, res_2.data["results"])
        self.assertNotIn(serializer_crew_1.data, res_2.data["results"])

    def test_crew_create_forbidden(self):

        payload = {
            "first_name": "TestFirstName",
            "last_name": "TestLastName"
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_crew_create(self):
        payload = {
            "first_name": "TestFirstName",
            "last_name": "TestLastName"
        }

        res = self.client.post(CREW_URL, payload)

        crew = Crew.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_crew_detail_route_not_available(self):
        crew = sample_crew()

        with self.assertRaises(NoReverseMatch):
            detail_url(crew.id)

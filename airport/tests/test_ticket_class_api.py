from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import TicketClass
from airport.serializers import TicketClassSerializer
from airport.tests.test_samples import (
    sample_ticket_class,
)


TICKET_CLASS_URL = reverse("airport:ticketclass-list")


def detail_url(ticket_class_id):
    return reverse(
        "airport:ticketclass-detail", args=[ticket_class_id]
    )


class UnauthenticatedTicketClassApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        sample_ticket_class()
        res = self.client.get(TICKET_CLASS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketClassApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_ticket_class_list(self):

        sample_ticket_class()

        res = self.client.get(TICKET_CLASS_URL)

        ticket_class = TicketClass.objects.all()
        serializer = TicketClassSerializer(ticket_class, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_ticket_class_filter_by_name(self):
        ticket_class_1 = sample_ticket_class(
            name="TestTicketClass1"
        )
        ticket_class_2 = sample_ticket_class(
            name="TestTicketClass2"
        )

        res = self.client.get(
            TICKET_CLASS_URL,
            {
                "name": f"{ticket_class_1.name}"
            }
        )


        serializer_ticket_class_1 = TicketClassSerializer(ticket_class_1)
        serializer_ticket_class_2 = TicketClassSerializer(ticket_class_2)

        self.assertIn(serializer_ticket_class_1.data, res.data["results"])
        self.assertNotIn(serializer_ticket_class_2.data, res.data["results"])

    def test_ticket_class_create_forbidden(self):

        payload = {
            "name": "TestTicketClass",
            "price_multiplier": "1.20",
        }

        res = self.client.post(TICKET_CLASS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTicketClassApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_ticket_class_create(self):
        payload = {
            "name": "TestTicketClass",
            "price_multiplier": "1.20",
        }

        res = self.client.post(TICKET_CLASS_URL, payload)

        ticket_class = TicketClass.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "price_multiplier":
                self.assertEqual(
                    Decimal(payload[key]),
                    getattr(ticket_class, key)
                )
            else:
                self.assertEqual(payload[key], getattr(ticket_class, key))

    def test_ticket_class_detail_route_not_available(self):
        ticket_class = sample_ticket_class()

        with self.assertRaises(NoReverseMatch):
            detail_url(ticket_class.id)

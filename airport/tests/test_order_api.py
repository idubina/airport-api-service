from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order, Ticket
from airport.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer
)
from airport.tests.test_samples import (
    OrderTicketSamples
)


ORDER_URL = reverse("airport:order-list")


def detail_url(order_id):
    return reverse(
        "airport:order-detail", args=[order_id]
    )


class UnauthenticatedOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.order_sample = OrderTicketSamples()

    def test_auth_required(self):
        user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )

        order = Order.objects.create(
            user=user
        )

        self.order_sample.sample_ticket_1(order)
        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

        self.order_sample = OrderTicketSamples()

    def test_get_order_list(self):
        user_2 = get_user_model().objects.create_user(
            email="testuser2@user.com",
            password="test-user2123"
        )

        order_user = Order.objects.create(user=self.user)

        order_not_user = Order.objects.create(user=user_2)

        self.order_sample.sample_ticket_1(order_user)
        self.order_sample.sample_ticket_2(order_not_user)

        res = self.client.get(ORDER_URL)

        user_orders = Order.objects.filter(user=self.user)
        other_orders = Order.objects.filter(user=user_2)
        serializer_user_orders = OrderListSerializer(user_orders, many=True)
        serializer_other_orders = OrderListSerializer(other_orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for order in serializer_user_orders.data:
            self.assertIn(order, res.data["results"])

        for order in serializer_other_orders.data:
            self.assertNotIn(order, res.data["results"])

    def test_retrieve_order_detail(self):
        user_2 = get_user_model().objects.create_user(
            email="testuser2@user.com",
            password="test-user2123"
        )

        order_user = Order.objects.create(user=self.user)

        order_not_user = Order.objects.create(user=user_2)

        self.order_sample.sample_ticket_1(order_user)
        self.order_sample.sample_ticket_2(order_not_user)

        res_1 = self.client.get(detail_url(order_user.id))
        res_2 = self.client.get(detail_url(order_not_user.id))

        serializer = OrderRetrieveSerializer(order_user)

        self.assertEqual(res_2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(serializer.data, res_1.data)

    def test_order_create(self):

        payload = {
            "tickets": [
                {
                    "row": 2,
                    "seat": 3,
                    "flight": self.order_sample.flight_1.id,
                    "ticket_class":  self.order_sample.ticket_class.id,
                },
                {
                    "row": 3,
                    "seat": 3,
                    "flight": self.order_sample.flight_1.id,
                    "ticket_class": self.order_sample.ticket_class.id,
                }
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        order = Order.objects.get(id=res.data["id"])

        self.assertEqual(self.user, order.user)
        self.assertEqual(order.tickets.count(), 2)

        payload_ticket_1 = payload["tickets"][0]
        payload_ticket_2 = payload["tickets"][1]

        created_tickets = order.tickets.order_by("row", "seat")

        created_ticket_1 = created_tickets[0]
        created_ticket_2 = created_tickets[1]

        self.assertEqual(payload_ticket_1["row"], created_ticket_1.row)
        self.assertEqual(payload_ticket_1["seat"], created_ticket_1.seat)
        self.assertEqual(payload_ticket_1["flight"], created_ticket_1.flight.id)
        self.assertEqual(payload_ticket_1["ticket_class"], created_ticket_1.ticket_class.id)

        self.assertEqual(payload_ticket_2["row"], created_ticket_2.row)
        self.assertEqual(payload_ticket_2["seat"], created_ticket_2.seat)
        self.assertEqual(payload_ticket_2["flight"], created_ticket_2.flight.id)
        self.assertEqual(payload_ticket_2["ticket_class"], created_ticket_2.ticket_class.id)

        expected_price = (
            self.order_sample.flight_1.base_price
            * self.order_sample.ticket_class.price_multiplier
        )

        self.assertEqual(created_ticket_1.price, expected_price)
        self.assertEqual(created_ticket_2.price, expected_price)

    def test_order_filter_by_flight_id(self):

        order_1 = Order.objects.create(user=self.user)
        order_2 = Order.objects.create(user=self.user)

        ticket_1 = self.order_sample.sample_ticket_1(order_1)

        self.order_sample.sample_ticket_3(order_2)

        res = self.client.get(
            ORDER_URL,
            {
                "flight": ticket_1.flight.id
            }
        )

        serializer_1 = OrderListSerializer(order_1)
        serializer_2 = OrderListSerializer(order_2)

        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

class AdminOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.order_sample = OrderTicketSamples()

    def test_get_list_all_users_oders(self):
        user_2 = get_user_model().objects.create_user(
            email="testuser2@user.com",
            password="test-user2123"
        )

        order_user = Order.objects.create(user=self.user)

        order_not_user = Order.objects.create(user=user_2)

        self.order_sample.sample_ticket_1(order_user)
        self.order_sample.sample_ticket_2(order_not_user)

        res = self.client.get(ORDER_URL)

        user_orders = Order.objects.filter(user=self.user)
        other_orders = Order.objects.filter(user=user_2)
        serializer_user_orders = OrderListSerializer(user_orders, many=True)
        serializer_other_orders = OrderListSerializer(other_orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for order in serializer_user_orders.data:
            self.assertIn(order, res.data["results"])

        for order in serializer_other_orders.data:
            self.assertIn(order, res.data["results"])

    def test_order_filter_by_user_ids(self):
        user_2 = get_user_model().objects.create_user(
            email="testuser2@user.com",
            password="test-user2123"
        )

        user_3 = get_user_model().objects.create_user(
            email="testuser3@user.com",
            password="test-user3123"
        )

        order_user_1 = Order.objects.create(user=self.user)

        order_user_2 = Order.objects.create(user=user_2)

        order_user_3 = Order.objects.create(user=user_3)

        self.order_sample.sample_ticket_1(order_user_1)
        self.order_sample.sample_ticket_2(order_user_2)
        self.order_sample.sample_ticket_3(order_user_3)

        res = self.client.get(
            ORDER_URL,
            {
                "users": f"{user_2.id},{user_3.id}"
            }
        )

        serializer_1 = OrderListSerializer(order_user_1)
        serializer_2 = OrderListSerializer(order_user_2)
        serializer_3 = OrderListSerializer(order_user_3)

        self.assertIn(serializer_2.data, res.data["results"])
        self.assertIn(serializer_3.data, res.data["results"])
        self.assertNotIn(serializer_1.data, res.data["results"])

    def test_order_delete_not_allowed(self):

        order = Order.objects.create(user=self.user)
        self.order_sample.sample_ticket_1(order)

        res = self.client.delete(detail_url(order.id))

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_order_update_not_allowed(self):

        order = Order.objects.create(user=self.user)
        self.order_sample.sample_ticket_1(order)

        payload = {
            "tickets": [
                {
                    "row": 5,
                    "seat": 10,
                    "flight": self.order_sample.flight_1.id,
                    "ticket_class": self.order_sample.ticket_class.id,
                }
            ]
        }

        res = self.client.patch(detail_url(order.id), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

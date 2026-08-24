from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Route
from airport.serializers import (
    RouteListSerializer,
    RouteRetrieveSerializer,
)
from airport.tests.test_samples import (
    sample_country,
    sample_city,
    sample_airport,
    base_sample_route,
    sample_route_1,
    sample_route_2,
)


ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


class UnauthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        base_sample_route()
        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_route_list(self):

        base_sample_route()

        res = self.client.get(ROUTE_URL)

        airports = Route.objects.all()
        serializer = RouteListSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_route_detail(self):

        route = base_sample_route()

        res = self.client.get(detail_url(route.id))

        serializer = RouteRetrieveSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_route_filter_by_source_id(self):

        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"source": route_1.source.id}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_filter_by_source_name(self):
        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"source_name": route_1.source.name}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_filter_by_source_city_name(self):
        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"source_city": route_1.source.closest_big_city.name}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_filter_by_source_country_name(self):
        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"source_country": route_1.source.closest_big_city.country.name}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_filter_by_destination_id(self):
        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"destination": route_1.destination.id}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_filter_by_destination_name(self):
        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"destination_name": route_1.destination.name}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_filter_by_destination_city_name(self):
        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"destination_city": route_1.destination.closest_big_city.name}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_filter_by_destination_country_name(self):
        route_1 = sample_route_1()
        route_2 = sample_route_2()

        res = self.client.get(
            ROUTE_URL,
            {"destination_country": route_1.destination.closest_big_city.country.name}
        )

        serializer_route_1 = RouteListSerializer(route_1)
        serializer_route_2 = RouteListSerializer(route_2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_route_create_forbidden(self):

        payload = {
            "source": sample_airport().id,
            "destination": sample_airport(
                name="TestDestinationAirport",
                city=sample_city(
                    name="TestDestinationCity",
                    country=sample_country(
                        name="TestDestinationCountry"
                    )
                )
            ).id,
           "distance": 133
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_route_create(self):

        payload = {
            "source": sample_airport().id,
            "destination": sample_airport(
                name="TestDestinationAirport",
                city=sample_city(
                    name="TestDestinationCity",
                    country=sample_country(
                        name="TestDestinationCountry"
                    )
                )
            ).id,
            "distance": 133
        }

        res = self.client.post(ROUTE_URL, payload)

        route = Route.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "source":
                self.assertEqual(
                    payload[key],
                    getattr(route, "source_id")
                )
            elif key == "destination":
                self.assertEqual(
                    payload[key],
                    getattr(route, "destination_id")
                )
            else:
                self.assertEqual(payload[key], getattr(route, key))

    def test_route_delete_not_allowed(self):

        route = base_sample_route()

        res = self.client.delete(detail_url(route.id))

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_route_update_not_allowed(self):

        route = sample_route_1()

        payload = {
            "source": sample_airport().id,
            "destination": sample_airport(
                name="TestDestinationAirport",
                city=sample_city(
                    name="TestDestinationCity",
                    country=sample_country(
                        name="TestDestinationCountry"
                    )
                )
            ).id,
            "distance": 133
        }

        res = self.client.put(detail_url(route.id), payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

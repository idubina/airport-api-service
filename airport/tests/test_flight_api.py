from datetime import datetime
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Flight
from airport.serializers import (
    FlightListSerializer,
    FlightRetrieveSerializer
)
from airport.tests.test_samples import (
    sample_flight_1,
    sample_flight_2,
    base_sample_route,
    base_sample_airplane,
    sample_crew,
)


FLIGHT_URL = reverse("airport:flight-list")


def detail_url(flight_id):
    return reverse(
        "airport:flight-detail", args=[flight_id]
    )


class UnauthenticatedFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        sample_flight_1()
        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@user.com",
            password="test-user123"
        )
        self.client.force_authenticate(self.user)

    def test_get_flight_list(self):

        sample_flight_1()

        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.select_related(
            "route__source__closest_big_city__country",
            "route__destination__closest_big_city__country",
            "airplane__airplane_type",
        ).prefetch_related(
            "crew",
        ).annotate(
            tickets_available=(
                F("airplane__seats_in_row")
                * F("airplane__rows")
                - Count("tickets", distinct=True)
            )
        ).order_by("id")
        serializer = FlightListSerializer(flights, many=True)



        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_flight_detail(self):

        flight = sample_flight_1()

        res = self.client.get(detail_url(flight.id))

        serializer = FlightRetrieveSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_flight_filter_by_min_base_price(self):

        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        flight_1.base_price = 100
        flight_1.save()
        flight_2.base_price = 110
        flight_2.save()

        res = self.client.get(
            FLIGHT_URL,
            {
                "min_base_price": 105
            }
        )


        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_2.data["id"], result_ids)
        self.assertNotIn(serializer_flight_1.data["id"], result_ids)

    def test_flight_filter_by_max_base_price(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        flight_1.base_price = 100
        flight_1.save()
        flight_2.base_price = 110
        flight_2.save()

        res = self.client.get(
            FLIGHT_URL,
            {
                "max_base_price": 105
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_filter_by_source_city(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        res = self.client.get(
            FLIGHT_URL,
            {
                "source_city": (
                    f"{flight_1.route.source.closest_big_city.name}"
                )
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_filter_by_destination_city(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        res = self.client.get(
            FLIGHT_URL,
            {
                "destination_city": (
                    f"{flight_1.route.destination.closest_big_city.name}"
                )
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_filter_by_departure_date(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        res = self.client.get(
            FLIGHT_URL,
            {
                "departure_date": flight_1.departure_time.date().isoformat()
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_filter_by_arrival_date(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        res = self.client.get(
            FLIGHT_URL,
            {
                "arrival_date": flight_1.arrival_time.date().isoformat()
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_filter_by_crew_ids(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        crew_ids = ",".join(
            str(crew_id) for crew_id in flight_1.crew.values_list("id", flat=True)
        )

        res = self.client.get(
            FLIGHT_URL,
            {
                "crew": crew_ids
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_filter_by_route_id(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        res = self.client.get(
            FLIGHT_URL,
            {
                "route": flight_1.route.id
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_filter_by_airplane_id(self):
        flight_1 = sample_flight_1()
        flight_2 = sample_flight_2()

        res = self.client.get(
            FLIGHT_URL,
            {
                "airplane": flight_1.airplane.id
            }
        )

        serializer_flight_1 = FlightListSerializer(flight_1)
        serializer_flight_2 = FlightListSerializer(flight_2)

        result_ids = [flight["id"] for flight in res.data["results"]]

        self.assertIn(serializer_flight_1.data["id"], result_ids)
        self.assertNotIn(serializer_flight_2.data["id"], result_ids)

    def test_flight_create_forbidden(self):

        payload = {
            "route": base_sample_route().id,
            "airplane": base_sample_airplane().id,
            "departure_time": timezone.make_aware(
                datetime(2026, 7, 12, 10, 0)
            ),
            "arrival_time": timezone.make_aware(
                datetime(2026, 7, 12, 20, 0)
            ),
            "base_price": 170,
            "crew": [
                sample_crew(
                    first_name="TestFirstName1",
                    last_name="TestLastName1"
                ).id,
                sample_crew(
                    first_name="TestFirstName2",
                    last_name="TestLastName2"
                ).id,
            ]
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_delete_forbidden(self):

        flight = sample_flight_1()

        res = self.client.delete(detail_url(flight.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_update_not_allowed(self):

        flight = sample_flight_2()

        payload = {
            "route": base_sample_route().id,
            "airplane": base_sample_airplane().id,
            "departure_time": timezone.make_aware(
                datetime(2026, 8, 12, 10, 0)
            ),
            "arrival_time": timezone.make_aware(
                datetime(2026, 8, 12, 20, 0)
            ),
            "base_price": 170,
            "crew": [
                sample_crew(
                    first_name="TestFirstName10",
                    last_name="TestLastName10"
                ).id,
                sample_crew(
                    first_name="TestFirstName21",
                    last_name="TestLastName21"
                ).id,
            ]
        }

        res = self.client.put(detail_url(flight.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testadmin@admin.com",
            password="test-admin123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_flight_create(self):

        payload = {
            "route": base_sample_route().id,
            "airplane": base_sample_airplane().id,
            "departure_time": timezone.make_aware(
                datetime(2026, 7, 12, 10, 0)
            ),
            "arrival_time": timezone.make_aware(
                datetime(2026, 7, 12, 20, 0)
            ),
            "base_price": 170,
            "crew": [
                sample_crew(
                    first_name="TestFirstName1",
                    last_name="TestLastName1"
                ).id,
                sample_crew(
                    first_name="TestFirstName2",
                    last_name="TestLastName2"
                ).id,
            ]
        }

        res = self.client.post(FLIGHT_URL, payload)

        flight = Flight.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(payload["route"], flight.route_id)
        self.assertEqual(payload["airplane"], flight.airplane_id)
        self.assertEqual(payload["base_price"], flight.base_price)
        self.assertEqual(payload["departure_time"], flight.departure_time)
        self.assertEqual(payload["arrival_time"], flight.arrival_time)
        self.assertEqual(
            sorted(payload["crew"]),
            sorted(list(flight.crew.values_list("id", flat=True)))
        )

    def test_flight_delete(self):

        flight = sample_flight_1()

        res = self.client.delete(detail_url(flight.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_flight_update(self):

        flight = sample_flight_2()

        payload = {
            "route": base_sample_route().id,
            "airplane": base_sample_airplane().id,
            "departure_time": timezone.make_aware(
                datetime(2026, 8, 12, 10, 0)
            ),
            "arrival_time": timezone.make_aware(
                datetime(2026, 8, 12, 20, 0)
            ),
            "base_price": 170,
            "crew": [
                sample_crew(
                    first_name="TestFirstName10",
                    last_name="TestLastName10"
                ).id,
                sample_crew(
                    first_name="TestFirstName21",
                    last_name="TestLastName21"
                ).id,
            ]
        }

        res = self.client.put(
            detail_url(flight.id),
            payload,
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        flight.refresh_from_db()

        self.assertEqual(payload["route"], flight.route_id)
        self.assertEqual(payload["airplane"], flight.airplane_id)
        self.assertEqual(payload["base_price"], flight.base_price)
        self.assertEqual(payload["departure_time"], flight.departure_time)
        self.assertEqual(payload["arrival_time"], flight.arrival_time)
        self.assertEqual(
            sorted(payload["crew"]),
            sorted(list(flight.crew.values_list("id", flat=True)))
        )

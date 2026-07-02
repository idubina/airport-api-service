from datetime import datetime
from decimal import Decimal

from django.utils import timezone

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Ticket,
    TicketClass
)


def sample_country(**params):
    defaults = {
        "name": "TestCountry"
    }
    defaults.update(params)
    return Country.objects.create(**defaults)

def sample_city(**params):
    country = params.pop("country", None)

    if country is None:
        country = sample_country()

    defaults = {
        "name": "TestCity",
        "country": country
    }
    defaults.update(params)
    return City.objects.create(**defaults)

def sample_airport(**params):
    city = params.pop("city", None)

    if city is None:
        city = sample_city()

    defaults = {
        "name": "TestAirport",
        "closest_big_city": city
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)

def sample_route_1():
    return Route.objects.create(
        source=sample_airport(
            name="TestSourceAirport1",
            city=sample_city(
                name="TestSourceCity1",
                country=sample_country(
                    name="TestSourceCountry1"
                )
            )
        ),
        destination=sample_airport(
            name="TestDestinationAirport1",
            city=sample_city(
                name="TestDestinationCity1",
                country=sample_country(
                    name="TestDestinationCountry1"
                )
            )
        ),
        distance=100,
    )

def sample_route_2():
    return Route.objects.create(
        source=sample_airport(
            name="TestSourceAirport2",
            city=sample_city(
                name="TestSourceCity2",
                country=sample_country(
                    name="TestSourceCountry2"
                )
            )
        ),
        destination=sample_airport(
            name="TestDestinationAirport2",
            city=sample_city(
                name="TestDestinationCity2",
                country=sample_country(
                    name="TestDestinationCountry2"
                )
            )
        ),
        distance=100,
    )


def base_sample_route(**params):

    source = params.pop("source", None)
    destination = params.pop("destination", None)

    if source is None:
        source = sample_airport(
            name="TestSourceAirport",
            city=sample_city(
                name="TestSourceCity",
                country=sample_country(
                    name="TestSourceCountry"
                )
            )
        )

    if destination is None:
        destination = sample_airport(
            name="TestDestinationAirport",
            city=sample_city(
                name="TestDestinationCity",
                country=sample_country(
                    name="TestDestinationCountry"
                )
            )
        )

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 120
    }
    defaults.update(params)
    return Route.objects.create(**defaults)

def sample_crew(**params):

    defaults = {
        "first_name": "TestFirstName",
        "last_name": "TestLastName",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)

def sample_airplane_type(**params):

    defaults = {"name": "TestAirplaneType"}

    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane_1():
    return Airplane.objects.create(
        name="TestAirplane1",
        rows=70,
        seats_in_row=6,
        airplane_type=sample_airplane_type(
            name="TestAirplaneType1"
        )
    )

def sample_airplane_2():
    return Airplane.objects.create(
        name="TestAirplane2",
        rows=70,
        seats_in_row=6,
        airplane_type=sample_airplane_type(
            name="TestAirplaneType2"
        )
    )

def base_sample_airplane(**params):
    airplane_type = params.pop("airplane_type", None)

    if airplane_type is None:
        airplane_type = sample_airplane_type()

    defaults = {
        "name": "TestAirplane",
        "rows": 70,
        "seats_in_row": 6,
        "airplane_type": airplane_type
    }

    defaults.update(params)
    return Airplane.objects.create(**defaults)

def sample_flight_1():
    flight =  Flight.objects.create(
        route=sample_route_1(),
        airplane=sample_airplane_1(),
        departure_time=timezone.make_aware(
            datetime(2026, 7, 1, 10, 0)
        ),
        arrival_time=timezone.make_aware(
            datetime(2026, 7, 1, 12, 30)
        ),
        base_price=170,
    )

    crew_1 = sample_crew(
        first_name="TestFirstName1",
        last_name="TestLastName1",
    )

    flight.crew.add(crew_1)

    crew_2 = sample_crew(
        first_name="TestFirstName2",
        last_name="TestLastName2",
    )

    flight.crew.add(crew_2)

    return flight


def sample_flight_2():
    flight = Flight.objects.create(
        route=sample_route_2(),
        airplane=sample_airplane_2(),
        departure_time=timezone.make_aware(
            datetime(2026, 7, 12, 10, 0)
        ),
        arrival_time=timezone.make_aware(
            datetime(2026, 7, 12, 12, 30)
        ),
        base_price=170,
    )

    crew_1 = sample_crew(
        first_name="TestFirstName3",
        last_name="TestLastName3",
    )

    flight.crew.add(crew_1)

    crew_2 = sample_crew(
        first_name="TestFirstName4",
        last_name="TestLastName4",
    )

    flight.crew.add(crew_2)

    return flight

def sample_ticket_class(**params):
    defaults = {
        "name": "TestTicketClass",
        "price_multiplier": Decimal("1.20")
    }
    defaults.update(params)
    return TicketClass.objects.create(**defaults)

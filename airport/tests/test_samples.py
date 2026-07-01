from tkinter.font import names

from airport.models import (
    Country,
    City,
    Airport,
    Route,
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
    defaults.update(**params)
    return Route.objects.create(**defaults)


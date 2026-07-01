from airport.models import (
    Country,
    City,
    Airport,
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

from airport.models import (
    Country,
    City,
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

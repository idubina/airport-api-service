from airport.models import (
    Country,
)


def sample_country(**params):
    defaults = {
        "name": "TestCountry"
    }
    defaults.update(params)
    return Country.objects.create(**defaults)

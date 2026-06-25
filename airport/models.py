from django.db import models
from django.db.models import Q, F


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country,
        related_name="cities",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "cities"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "country"],
                name="unique_city_per_country"
            )
        ]

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(
        City,
        related_name="airports",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return (
            f"{self.name}"
            f" - {self.closest_big_city}"
            f" ({self.closest_big_city.country})"
        )


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        related_name="routes_from",
        on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Airport,
        related_name="routes_to",
        on_delete=models.CASCADE
    )
    distance = models.PositiveIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["source", "destination"])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_route_source_destination"
            ),
            models.CheckConstraint(
                check=~Q(source=F("destination")),
                name="source_and_destination_are_different"
            )
        ]

    def __str__(self):
        return (
            f"{self.source.closest_big_city}"
            f" - {self.destination.closest_big_city}"
            f" ({self.distance} km)"
        )

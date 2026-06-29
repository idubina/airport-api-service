from django.conf import settings
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
                condition=~Q(source=F("destination")),
                name="source_and_destination_are_different"
            )
        ]

    def __str__(self):
        return (
            f"{self.source.closest_big_city}"
            f" - {self.destination.closest_big_city}"
            f" ({self.distance} km)"
        )


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_rows = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        related_name="airplanes",
        on_delete=models.CASCADE
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_rows

    def __str__(self):
        return f"{self.name} ({self.airplane_type})"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        related_name="flights",
        on_delete=models.CASCADE
    )
    airplane = models.ForeignKey(
        Airplane,
        related_name="flights",
        on_delete=models.CASCADE
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )
    crew = models.ManyToManyField(
        Crew,
        related_name="flights",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(departure_time__lt=F("arrival_time")),
                name="departure_time_before_arrival_time"
            )
        ]

    def __str__(self):
        return f"{self.route} [time: {self.departure_time}]"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class TicketClass(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price_multiplier = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        verbose_name_plural = "ticket_classes"

    def __str__(self):
        return self.name


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        related_name="tickets",
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order,
        related_name="tickets",
        on_delete=models.CASCADE
    )
    ticket_class = models.ForeignKey(
        TicketClass,
        related_name="tickets",
        on_delete=models.PROTECT
    )
    price = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "row", "seat"],
                name="unique_ticket_seat"
            )
        ]
        ordering = ["seat"]

    def __str__(self):
        return f"{self.flight} - seat: {self.seat} [{self.ticket_class}]"

    @staticmethod
    def validate_seat(seat: int, num_seats: int, error_to_raise):
        if not (1 <= seat <= num_seats):
            raise error_to_raise(
                {"seat": f"seat must be in range [1, {num_seats}], not {seat}"}
            )

    def clean(self):
        self.validate_seat(
            self.seat, self.flight.airplane.capacity, ValueError
        )

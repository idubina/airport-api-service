from django.db import transaction
from rest_framework import serializers
from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    TicketClass,
    Ticket
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            "id",
            "name",
        )


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = (
            "id",
            "name",
            "country",
        )


class CityListRetrieveSerializer(CitySerializer):
    country = serializers.CharField(source="country.name", read_only=True)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
            "image"
        )


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.CharField(
        source="closest_big_city.name",
        read_only=True
    )


class AirportRetrieveSerializer(AirportSerializer):
    closest_big_city = CityListRetrieveSerializer(read_only=True)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance"
        )


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField(read_only=True)
    destination = serializers.StringRelatedField(read_only=True)


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportRetrieveSerializer(read_only=True)
    destination = AirportRetrieveSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "full_name",
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "capacity",
            "seats_in_rows",
            "airplane_type",
            "image"
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField(read_only=True)


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "base_price",
            "crew",
        )


class FlightListSerializer(serializers.ModelSerializer):
    airplane = serializers.StringRelatedField(read_only=True)
    route = serializers.StringRelatedField(read_only=True)
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    tickets_available = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "base_price",
            "crew",
            "tickets_available",
        )


class TicketSeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = (
            "seat",
            "row",
        )


class FlightRetrieveSerializer(serializers.ModelSerializer):
    airplane = AirplaneSerializer(read_only=True)
    route = RouteListSerializer(read_only=True)
    crew = CrewSerializer(read_only=True, many=True)
    taken_places = TicketSeatSerializer(
        source="tickets",
        many=True,
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "base_price",
            "crew",
            "taken_places",
        )


class TicketClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketClass
        fields = (
            "id",
            "name",
            "price_multiplier",
        )


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "ticket_class",
            "price"
        )
        read_only_fields = ("id", "price",)

    def validate(self, attrs):
        Ticket.validate_seat(
            attrs["seat"],
            attrs["flight"].airplane.capacity,
            serializers.ValidationError
        )


class TicketListSerializer(TicketSerializer):
    ticket_class = serializers.StringRelatedField(read_only=True)
    flight = serializers.StringRelatedField(read_only=True)


class TicketRetrieveSerializer(TicketSerializer):
    ticket_class = TicketClassSerializer(read_only=True)
    flight = FlightListSerializer(
        read_only=True,
    )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets",
        )

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = super().create(validated_data)

            for ticket_data in tickets_data:
                flight = ticket_data["flight"]
                ticket_class = ticket_data["ticket_class"]
                ticket_data["price"] = (
                    flight.base_price * ticket_class.price_multiplier
                )
                Ticket.objects.create(order=order, **ticket_data)

            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(read_only=True, many=True)


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketRetrieveSerializer(read_only=True, many=True)


class AirplaneImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "image",
        )


class AirportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "image",
        )

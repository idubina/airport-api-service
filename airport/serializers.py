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
            "seats_in_rows",
            "airplane_type",
            "capacity",
        )


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
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "user",
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
            "order",
            "ticket_class",
            "price"
        )

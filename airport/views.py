from rest_framework import viewsets

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
from airport.serializers import (
    CountrySerializer,
    CityListRetrieveSerializer,
    CitySerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    CrewSerializer,
    CrewListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketClassSerializer,
    TicketSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve",):
            return CityListRetrieveSerializer
        return CitySerializer

    def get_queryset(self):
        queryset = self.queryset
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(country__name__iexact=country)
        if self.action == "list":
            queryset = queryset.select_related("country")
        return queryset


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportRetrieveSerializer
        return AirportSerializer

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        city = self.request.query_params.get("city")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(closest_big_city__name__iexact=city)

        if self.action == "list":
            queryset = queryset.select_related("closest_big_city")

        if self.action == "retrieve":
            queryset = queryset.select_related("closest_big_city__country")

        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset

        source_name = self.request.query_params.get("source_name")
        source_city = self.request.query_params.get("source_city")
        source_country = self.request.query_params.get("source_country")
        destination_name = self.request.query_params.get("destination_name")
        destination_city = self.request.query_params.get("destination_city")
        destination_country = self.request.query_params.get(
            "destination_country"
        )

        if source_name:
            queryset = queryset.filter(
                source__name__icontains=source_name
            )
        if source_city:
            lookup = "source__closest_big_city__name__icontains"
            queryset = queryset.filter(
                **{lookup: source_city}
            )
        if source_country:
            lookup = "source__closest_big_city__country__name__icontains"
            queryset = queryset.filter(
                **{lookup: source_country}
            )

        if destination_name:
            queryset = queryset.filter(
                destination__name__icontains=destination_name
            )
        if destination_city:
            lookup = "destination__closest_big_city__name__icontains"
            queryset = queryset.filter(
                **{lookup: destination_city}
            )
        if destination_country:
            lookup = "destination__closest_big_city__country__name__icontains"
            queryset = queryset.filter(
                **{lookup: destination_country}
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "destination__closest_big_city__country",
                "source__closest_big_city__country"
            )

        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        first_name = self.request.query_params.get("first_name")
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        last_name = self.request.query_params.get("last_name")
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.all()


class FlightViewSet(viewsets.ModelViewSet):
    serializer_class = FlightSerializer
    queryset = Flight.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class TicketClassViewSet(viewsets.ModelViewSet):
    serializer_class = TicketClassSerializer
    queryset = TicketClass.objects.all()


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

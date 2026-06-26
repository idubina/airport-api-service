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
    CrewSerializer,
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
    serializer_class = RouteSerializer
    queryset = Route.objects.all()


class CrewViewSet(viewsets.ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


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

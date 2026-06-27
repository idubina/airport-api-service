from datetime import datetime

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
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
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

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("airplane_type")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if airplane_type:
            queryset = queryset.filter(
                airplane_type__name__icontains=airplane_type
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("airplane_type")

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    serializer_class = FlightSerializer
    queryset = Flight.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightRetrieveSerializer

        return self.serializer_class

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        min_base_price = self.request.query_params.get("min_base_price")
        max_base_price = self.request.query_params.get("max_base_price")

        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")

        crew = self.request.query_params.get("crew")

        departure_date = self.request.query_params.get("departure_date")
        arrival_date = self.request.query_params.get("arrival_date")

        if min_base_price:
            queryset = queryset.filter(base_price__gte=min_base_price)

        if max_base_price:
            queryset = queryset.filter(base_price__lte=max_base_price)

        if source_city:
            lookup = "route__source__closest_big_city__name__icontains"
            queryset = queryset.filter(
                **{lookup: source_city}
            )

        if destination_city:
            lookup = "route__destination__closest_big_city__name__icontains"
            queryset = queryset.filter(
                **{lookup: destination_city}
            )

        if crew:
            crew_ids = self._params_to_ints(crew)
            queryset = queryset.filter(crew__id__in=crew_ids)

        if departure_date:
            departure_date = datetime.strptime(
                departure_date,
                "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(departure_time__date=departure_date)

        if arrival_date:
            arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival_date)

        if self.action in ("list", "retrieve"):
            queryset = (
                queryset.select_related(
                    "route__source__closest_big_city__country",
                    "route__destination__closest_big_city__country",
                    "airplane__airplane_type"
                )
                .prefetch_related("crew")
            )

        route = self.request.query_params.get("route")
        airplane = self.request.query_params.get("airplane")

        if route:
            queryset = queryset.filter(route_id=route)

        if airplane:
            queryset = queryset.filter(airplane_id=airplane)

        return queryset.distinct()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class TicketClassViewSet(viewsets.ModelViewSet):
    serializer_class = TicketClassSerializer
    queryset = TicketClass.objects.all()


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

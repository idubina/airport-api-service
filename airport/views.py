from datetime import datetime

from django.db.models import Prefetch, Count, F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

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
    Ticket,
)
from airport.serializers import (
    CountrySerializer,
    CityListRetrieveSerializer,
    CitySerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    AirportImageSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    CrewSerializer,
    CrewListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneImageSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
    TicketClassSerializer,
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="country",
                description="Filter by country name",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of cities."""
        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportRetrieveSerializer
        if self.action == "upload_airport_image":
            return AirportImageSerializer
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by airport name",
                type=str,
            ),
            OpenApiParameter(
                name="city",
                description="Filter by city name",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of airports."""
        return super().list(request, *args, **kwargs)

    @action(
        methods=["post"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser, ]
    )
    def upload_airport_image(self, request, pk=None):

        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        destination = self.request.query_params.get("destination")
        source = self.request.query_params.get("source")

        if destination:
            queryset = queryset.filter(destination_id=destination)

        if source:
            queryset = queryset.filter(source_id=source)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "destination__closest_big_city__country",
                "source__closest_big_city__country"
            )

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source",
                description="Filter by source id",
                type=int,
            ),
            OpenApiParameter(
                name="source_name",
                description="Filter by source airport name",
                type=str,
            ),
            OpenApiParameter(
                name="source_city",
                description="Filter by source city",
                type=str,
            ),
            OpenApiParameter(
                name="source_country",
                description="Filter by source country",
                type=str,
            ),
            OpenApiParameter(
                name="destination",
                description="Filter by destination id",
                type=int,
            ),
            OpenApiParameter(
                name="destination_name",
                description="Filter by destination airport name",
                type=str,
            ),
            OpenApiParameter(
                name="destination_city",
                description="Filter by destination city",
                type=str,
            ),
            OpenApiParameter(
                name="destination_country",
                description="Filter by destination country",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of routes."""
        return super().list(request, *args, **kwargs)


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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="first_name",
                description="Filter by first name",
                type=str,
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter by last name",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of crews."""
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by Airplane Type name",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of airplane types."""
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        if self.action == "upload_airplane_image":
            return AirplaneImageSerializer
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by Airplane name",
                type=str,
            ),
            OpenApiParameter(
                name="airplane_type",
                description="Filter by Airplane type",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of airplanes."""
        return super().list(request, *args, **kwargs)

    @action(
        methods=["post"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser,]
    )
    def upload_airplane_image(self, request, pk=None):

        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                .prefetch_related("crew", "tickets")
            )
            if self.action == "list":
                queryset = queryset.annotate(
                    tickets_available=(
                        F("airplane__seats_in_rows")
                        * F("airplane__rows")
                        - Count("tickets", distinct=True)
                    )
                ).order_by("id")

        route = self.request.query_params.get("route")
        airplane = self.request.query_params.get("airplane")

        if route:
            queryset = queryset.filter(route_id=route)

        if airplane:
            queryset = queryset.filter(airplane_id=airplane)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="min_base_price",
                description="Filter by flight min base price",
                type=int,
            ),
            OpenApiParameter(
                name="max_base_price",
                description="Filter by flight max base price",
                type=int,
            ),
            OpenApiParameter(
                name="source_city",
                description="Filter by source airport city",
                type=str,
            ),
            OpenApiParameter(
                name="destination_city",
                description="Filter by destination airport city",
                type=str,
            ),
            OpenApiParameter(
                name="crew",
                description="Filter by crew ids (ex. ?crew=2,3)",
                type={
                    "type": "array",
                    "items": {"type": "integer"}
                },
            ),
            OpenApiParameter(
                name="departure_date",
                description=(
                    "Filter by departure date"
                    " in YYYY-MM-DD format"
                ),
                type=str,
            ),
            OpenApiParameter(
                name="arrival_date",
                description=(
                    "Filter by arrival date"
                    " in YYYY-MM-DD format"
                ),
                type=str,
            ),
            OpenApiParameter(
                name="route",
                description="Filter by route id",
                type=int,
            ),
            OpenApiParameter(
                name="airplane",
                description="Filter by airplane id",
                type=int,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of flights."""
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):

        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderRetrieveSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        else:
            users = self.request.query_params.get("users")
            if users:
                user_ids = self._params_to_ints(users)
                queryset = queryset.filter(user__id__in=user_ids)

        flight = self.request.query_params.get("flight")

        if flight:
            queryset = queryset.filter(tickets__flight__id=flight)

        if self.action in ("list", "retrieve"):
            tickets_queryset = Ticket.objects.select_related(
                "ticket_class",
                "flight__route__source__closest_big_city__country",
                "flight__route__destination__closest_big_city__country",
                "flight__airplane__airplane_type",
            ).prefetch_related(
                "flight__crew",
            )

            queryset = queryset.prefetch_related(
                Prefetch("tickets", queryset=tickets_queryset)
            )
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="flight",
                description="Filter by ticket flight id",
                type=int,
            ),
            OpenApiParameter(
                name="users",
                description="Filter by users",
                type={
                    "type": "array",
                    "items": {"type": "integer"}
                },
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of orders."""
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketClassViewSet(viewsets.ModelViewSet):
    serializer_class = TicketClassSerializer
    queryset = TicketClass.objects.all()

    def get_queryset(self):

        queryset = self.queryset

        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by ticket class name",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of ticket classes."""
        return super().list(request, *args, **kwargs)

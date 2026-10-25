
from django.db import transaction
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event, Reservation
from .serializers import EventSerializer, ReservationSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()

        status_param = self.request.query_params.get('status')
        venue_param = self.request.query_params.get('venue')

        if status_param:
            queryset = queryset.filter(status=status_param)

        if venue_param:
            queryset = queryset.filter(venue__icontains=venue_param)

        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = Reservation.objects.select_related('event')

        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        requested_event = serializer.validated_data['event']
        seats = serializer.validated_data['seats_reserved']

        with transaction.atomic():
            event = Event.objects.select_for_update().get(
                pk=requested_event.pk
            )

            if event.status not in ('upcoming', 'ongoing'):
                return Response(
                    {'error': f'Cannot reserve seats for a {event.status} event.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated = Event.objects.filter(
                pk=event.pk,
                available_seats__gte=seats,
            ).update(available_seats=F('available_seats') - seats)

            if not updated:
                event.refresh_from_db()
                return Response(
                    {'non_field_errors': [
                        f'Only {event.available_seats} seat(s) available.'
                    ]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            reservation = serializer.save()

        output = self.get_serializer(reservation)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            reservation = self.get_queryset().select_for_update().get(pk=pk)

            if reservation.status == 'cancelled':
                return Response(
                    {'error': 'Already cancelled.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            event = Event.objects.select_for_update().get(
                pk=reservation.event_id
            )

            Event.objects.filter(pk=event.pk).update(
                available_seats=F('available_seats') + reservation.seats_reserved
            )

            reservation.status = 'cancelled'
            reservation.save(update_fields=['status'])

        return Response(self.get_serializer(reservation).data)

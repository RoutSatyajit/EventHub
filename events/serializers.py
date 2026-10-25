
from rest_framework import serializers
from .models import Event, Reservation


class EventSerializer(serializers.ModelSerializer):
    reservations_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'venue',
            'date',
            'total_seats',
            'available_seats',
            'status',
            'created_at',
            'reservations_count',
        ]
        read_only_fields = ['id', 'created_at', 'reservations_count']

    def get_reservations_count(self, obj):
        return obj.reservations.filter(status='confirmed').count()

    def validate(self, data):
        total_seats = data.get(
            'total_seats',
            self.instance.total_seats if self.instance else 0
        )
        available_seats = data.get(
            'available_seats',
            self.instance.available_seats if self.instance else 0
        )

        if available_seats > total_seats:
            raise serializers.ValidationError(
                'available_seats cannot exceed total_seats.'
            )

        return data


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id',
            'event',
            'attendee_name',
            'attendee_email',
            'seats_reserved',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate_seats_reserved(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Must reserve at least 1 seat.'
            )
        return value

    def validate(self, data):
        event = data.get(
            'event',
            self.instance.event if self.instance else None
        )

        if event is None:
            return data

        seats_reserved = data.get(
            'seats_reserved',
            self.instance.seats_reserved if self.instance else 0
        )

        if self.instance is None:
            if event.status not in ('upcoming', 'ongoing'):
                raise serializers.ValidationError(
                    f'Cannot reserve seats for a {event.status} event.'
                )

            if seats_reserved > event.available_seats:
                raise serializers.ValidationError(
                    f'Only {event.available_seats} seat(s) available.'
                )

        return data

    def create(self, validated_data):
        # Seat deduction will be implemented safely in the
        # reservation workflow in the next steps.
        return Reservation.objects.create(**validated_data)

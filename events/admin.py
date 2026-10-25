
from django.contrib import admin
from .models import Event, Reservation


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'venue',
        'date',
        'total_seats',
        'available_seats',
        'status',
    )

    list_filter = ('status', 'date', 'venue')
    search_fields = ('title', 'venue')
    ordering = ('date',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event',
        'attendee_name',
        'attendee_email',
        'seats_reserved',
        'status',
        'created_at',
    )

    list_filter = ('status', 'created_at')
    search_fields = ('attendee_name', 'attendee_email')
    ordering = ('-created_at',)

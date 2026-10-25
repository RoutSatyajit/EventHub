# EventHub

EventHub is a Django REST Framework API for managing events and seat reservations. The development database is SQLite.

## Run the project

From the project root:

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install Django and Django REST Framework:

   ```powershell
   python -m pip install "Django>=5.2,<6.0" djangorestframework
   ```

3. Apply database migrations:

   ```powershell
   python manage.py migrate
   ```

4. Start the development server:

   ```powershell
   python manage.py runserver
   ```

The API is available at `http://127.0.0.1:8000/api/`. Django REST Framework's browsable API can be used from a browser, or the endpoints can be called with an HTTP client using JSON.

## API endpoints

All API routes are under `/api/`. The router API root is `GET /api/`.

### Events

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/events/` | List events. Optional `status` and `venue` query parameters filter by exact status and case-insensitive partial venue match, respectively. |
| `POST` | `/api/events/` | Create an event. Supply `title`, `venue`, `date`, `total_seats`, and `available_seats`; `status` is optional and defaults to `upcoming`. |
| `GET` | `/api/events/{id}/` | Retrieve one event, including its confirmed-reservation count. |
| `PUT` | `/api/events/{id}/` | Replace an event's editable fields. |
| `PATCH` | `/api/events/{id}/` | Partially update an event. |
| `DELETE` | `/api/events/{id}/` | Delete an event and, because reservations are linked with cascading deletion, its reservations. |

Event status values are `upcoming`, `ongoing`, `completed`, and `cancelled`. Available seats cannot exceed total seats.

### Reservations

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/reservations/` | List reservations. Optionally filter with `event_id`. |
| `POST` | `/api/reservations/` | Reserve seats for an event. Supply `event` (event ID), `attendee_name`, `attendee_email`, and `seats_reserved`. Reservations are accepted only for upcoming or ongoing events with enough seats. |
| `GET` | `/api/reservations/{id}/` | Retrieve one reservation. |
| `PUT` | `/api/reservations/{id}/` | Replace an existing reservation's editable fields. |
| `PATCH` | `/api/reservations/{id}/` | Partially update an existing reservation. |
| `DELETE` | `/api/reservations/{id}/` | Delete a reservation record. Unlike the cancel action, this does not return seats to the event. |
| `POST` | `/api/reservations/{id}/cancel/` | Cancel a reservation and return its reserved seats to the event. |

## Design decision

Reservation creation and cancellation use database transactions. When creating a reservation, the API conditionally decrements the event's available-seat count only if enough seats remain, then creates the reservation in the same transaction. This keeps seat counts and reservations consistent and helps prevent overbooking when requests overlap.

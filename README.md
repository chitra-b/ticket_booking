Backend Coding task - v1
"""
Write a REST API for a theater ticket booking system. The system should provide functionality for checking available seats, booking a seat, and temporarily reserving a seat with an expiry time.
The challenge includes implementing caching for seat availability and ensuring idempotent seat booking operations.

Requirements:
API Endpoints:
GET /theaters/{theaterId}/seats: Retrieves the current availability of seats for a specified theater.
POST /theaters/{theaterId}/book: Books a seat for a specified theater. This operation should be idempotent.
POST /theaters/{theaterId}/reserve: Temporarily reserves a seat for a specified theater with an expiry time.

Caching:
Implement caching for the GET /theaters/{theaterId}/seats endpoint to improve performance. The cache should be updated accordingly when a seat is booked or reserved.

Idempotency:
Ensure that booking a seat is an idempotent operation. This means if the booking request is repeated (e.g., due to network issues), it won't result in multiple bookings.

Temporary Reservation:
Allow seats to be temporarily reserved. If the reservation is not converted to a booking within a certain time frame, the reservation expires and the seat becomes available again.
"""

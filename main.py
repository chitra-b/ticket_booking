# Backend
# Coding
# task - v1
# """
# Write a REST API for a theater ticket booking system. The system should provide functionality for checking available seats, booking a seat, and temporarily reserving a seat with an expiry time.
# The challenge includes implementing caching for seat availability and ensuring idempotent seat booking operations.
#
# Requirements:
# API Endpoints:
# GET /theaters/{theaterId}/seats: Retrieves the current availability of seats for a specified theater.
# POST /theaters/{theaterId}/book: Books a seat for a specified theater. This operation should be idempotent.
# POST /theaters/{theaterId}/reserve: Temporarily reserves a seat for a specified theater with an expiry time.
#
# Caching:
# Implement caching for the GET /theaters/{theaterId}/seats endpoint to improve performance. The cache should be updated accordingly when a seat is booked or reserved.
#
# Idempotency:
# Ensure that booking a seat is an idempotent operation. This means if the booking request is repeated (e.g., due to network issues), it won't result in multiple bookings.
#
# Temporary Reservation:
# Allow seats to be temporarily reserved. If the reservation is not converted to a booking within a certain time frame, the reservation expires and the seat becomes available again.
# """

from pydantic import BaseModel
from fastapi import FastAPI
from typing import Literal, Optional, List
from fastapi import HTTPException
from datetime import datetime, timedelta
from fastapi_utils.tasks import repeat_every


app = FastAPI()

EXPIRY_IN_MINUTES = 10


class Theater(BaseModel):
    id : int
    no_of_seats: int
    no_of_seats_remaining: Optional[int] = None


class Booking(BaseModel):
    theater_id: int
    user_email: str
    booking_type: Literal["booked", "reserved"]
    no_of_seats : int
    expiry_time: Optional[datetime] = None

theaters = []
bookings = []

@app.post("/theaters", response_model=Theater)
def create_theater_data(theater: Theater):
    theater.no_of_seats_remaining = theater.no_of_seats
    theaters.append(theater)
    return theater

@app.get("/theaters", response_model=List[Theater])
def get_theaters():
    return theaters


@app.get("/theaters/{theaterId}/seats")
def get_seats_availability(theaterId: int):
    for each_theater in theaters:
        if each_theater.id == theaterId:
            return each_theater.no_of_seats_remaining

@app.post("/theaters/{theaterId}/book", response_model=Booking)
def create_booking(theaterId: int, booking : Booking):
    """
    1. Direct Booking
    2, Conversion from reservation to booking
    """
    if booking.id:
        # Conversion from reservation to booking
        if booking.expiry_time < datetime.now():
            raise HTTPException(status_code=400, detail="Bad request, Reserved seats are expired")
        for each_booking in bookings:
            if each_booking.id == booking.id:
                each_booking.booking_type = "booked"
                each_booking.expiry_time = None
    else:
        # Direct Booking
        for each_theater in theaters:
            if each_theater.no_of_seats_remaining <  booking.no_of_seats:
                raise HTTPException(status_code=400, detail="Bad request, seats are not available")
            if each_theater.id == theaterId:
                each_theater.no_of_seats_remaining = each_theater.no_of_seats_remaining - booking.no_of_seats
        bookings.append(booking)

    return booking

@app.post("/theaters/{theaterId}/reserve", response_model=Booking)
def create_reservation(theaterId: int, booking : Booking):
    for each_theater in theaters:
        if each_theater.no_of_seats_remaining <  booking.no_of_seats:
            raise HTTPException(status_code=400, detail="Bad request, seats are not available")
        if each_theater.id == theaterId:
            each_theater.no_of_seats_remaining = each_theater.no_of_seats_remaining - booking.no_of_seats
            booking.expiry_time = datetime.now() + timedelta(minutes=EXPIRY_IN_MINUTES)
    bookings.append(booking)
    return booking

@app.on_event("startup")
@repeat_every(seconds=60)  # 1 min
def remove_expired_reservation() -> None:
    for each_booking in bookings:
        if each_booking.booking_type == "reserved" and each_booking.expiry_time < datetime.now():
            each_booking.booking_type = "expired"
            each_booking.expiry_time = None
            theater_id = each_booking.theater_id
            for each_theater in theaters:
                if each_theater.id == theater_id:
                    each_theater.no_of_seats_remaining = each_theater.no_of_seats_remaining + each_booking.no_of_seats




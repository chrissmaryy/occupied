from datetime import datetime, timedelta
from app.db.db_manager import *
from app.db.reservation_rules import *

def create_reservation(user_id: int, start: datetime, length: int, is_private: bool) -> int:
    end = start + timedelta(minutes=length)
    conflicts = get_reservations_between(start, end)

    if conflicts:
        raise ValueError("Cannot create reservation, time blocked")
    
    reservation_id = create_reservation_entry(
        user_id,
        is_private,
        start,
        end
        )
    
    return(reservation_id)

def get_reservation(reservation_id: int):
    return get_reservation_by_id(reservation_id)

def get_reservations_per_day(day: datetime):
    return get_reservations_for_day(day.date().isoformat())

def get_reservations_per_user(user_id: int):
    return get_reservations_user(user_id)

def get_active_reservation(now: datetime | None = None):
    now = now or datetime.now()

    return get_active_reservation_entry(now)

def remaining_time(reservation_id: int) -> timedelta:
    return time_until_end(reservation_id)

def delete_reservation(reservation_id: int, user_id: int):
    if not can_edit(reservation_id, user_id):
        raise PermissionError("Not your reservation")
    delete_reservation_entry(reservation_id)

def start_reservation_early(reservation_id: int):
    reservation = get_reservation_by_id(reservation_id)

    now = datetime.now()

    # Konfliktcheck
    conflicts = get_reservations_between(
        now,
        reservation["start_time"]
    )

    if conflicts:
        raise ValueError("Cannot start early, time blocked")
    
    delta = reservation["start_time"] - now
    new_end = reservation["end_time"] - delta

    update_reservation_entry(
        reservation_id,
        reservation["is_private"],
        start_time=now,
        end_time=new_end
    )

def start_reservation_late(reservation_id: int, start_time: datetime):
    reservation = get_reservation_by_id(reservation_id)
    
    update_reservation_entry(
        reservation_id,
        reservation["is_private"],
        start_time,
        reservation["end_time"]
    )

def extend_reservation(reservation_id: int, new_end_time: datetime):
    reservation = get_reservation_by_id(reservation_id)

    conflicts = get_reservations_between(reservation["end_time"], new_end_time)
    conflicts = [
        r for r in conflicts
        if r[0] != reservation_id
    ]

    if conflicts:
        raise ValueError("Cannot extend, time blocked")

    update_reservation_entry(
        reservation_id,
        reservation["is_private"],
        reservation["start_time"],
        new_end_time
    )
    
def end_reservation_early(reservation_id: int, new_end_time: datetime):
    reservation = get_reservation_by_id(reservation_id)

    now = datetime.now()

    if now == new_end_time and now < reservation["start_time"]:
        raise ValueError("Cannot end now - reservation not started")
    
    update_reservation_entry(
        reservation_id,
        reservation["is_private"],
        reservation["start_time"],
        new_end_time
    )

def change_privacy(reservation_id: int, is_private: bool):
    reservation = get_reservation_by_id(reservation_id)

    update_reservation_entry(
        reservation_id,
        is_private,
        reservation["start_time"],
        reservation["end_time"]
    )

def update_reservation(reservation_id: int, user_id: int, is_private: bool, start_time: datetime, reservation_length: int):
    current = get_reservation_by_id(reservation_id)

    if not current:
        raise ValueError("Reservation not found")
    if not can_edit(reservation_id, user_id):
        raise PermissionError("Not your reservation")

    end_time = start_time + timedelta(minutes = reservation_length)

    if is_private != current[is_private]:
        change_privacy(reservation_id, is_private)

    if start_time < current["start_time"]:
        start_reservation_early(reservation_id)

    if end_time > current["end_time"]:
        extend_reservation(reservation_id, end_time)

    if end_time < current["end_time"]:
        end_reservation_early(reservation_id, end_time)

    if start_time > current["start_time"]:
        start_reservation_late(reservation_id, start_time)


    return get_reservation_by_id(reservation_id)



from reservation import Reservation

# Welche Reservation-Typen blockieren welche anderen Typen
BLOCK_MAP = {
    "Duschen": ["Duschen", "Zähne putzen", "Toilette kurz", "Toilette lang"],
    "Zähne putzen": ["Duschen", "Toilette lang"],
    "Toilette kurz": ["Duschen", "Toilette kurz", "Toilette lang"],
    "Toilette lang": ["Duschen", "Zähne putzen", "Toilette kurz", "Toilette lang"]
}

def can_book_type(new_reservation_type: int, existing_reservation_types: list[int]) -> bool:
    """
    Prüft, ob new_type in Gegenwart von existing_types erlaubt ist.
    """
    blocked = BLOCK_MAP.get(new_reservation_type, [])
    for t in existing_reservation_types:
        if t in blocked:
            return False
    return True

def overlaps(res_a: Reservation, res_b: Reservation) -> bool:
    return res_a.start_time < res_b.end_time and res_b.start_time < res_a.end_time

def can_start_early(reservation, now, conflicts):
    return len(conflicts) == 0

def can_edit(reservation_user_id: int, user_id: int) -> bool:
    if reservation_user_id == user_id:
        return True
    return False
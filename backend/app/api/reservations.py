from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import *
from app.services.reservation_service import *

router = APIRouter(prefix="/reservations", tags=["reservations"])

def get_current_user():
    return {"id": 1}

@router.post("/")
def create_reservation_endpoint(data: ReservationCreateRequest, current_user = Depends(get_current_user)):
    try:
        return create_reservation(
            current_user,
            data.start_time,
            data.end_time,
            data.type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, details=str(e))

@router.get("/{reservation_id}")
def get_reservation_endpoint(reservation_id: int):
    try:
         reservation = get_reservation(reservation_id=reservation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, details=str(e))
    
    if reservation is None:
        return HTTPException(status_code=404, details="Reservation not found")
    return reservation

@router.get("/day/{date}")
def get_reservations_for_day_endpoint(date: str):
    try:
         return get_reservations_per_day(date)
    except ValueError as e:
        raise HTTPException(status_code=400, details=str(e))

@router.get("/user")
def get_reservation_for_user_endpoint(current_user = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=400, details=str(e))

    try:
        return get_reservations_per_user(current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, details=str(e))

@router.put("/{reservation_id}")
def update_reservation_endpoint(reservation_id: int, data: ReservationUpdateRequest):
    try:
         reservation = update_reservation(
            reservation_id,
            data.type,
            data.start_time,
            data.end_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, details=str(e))
    
    if reservation is None:
        return HTTPException(status_code=404, details="Reservation not found")
    return reservation

@router.delete("/{reservation_id}")
def delete_reservation_endpoint(reservation_id: int, current_user = Depends(get_current_user)):
    try:
         reservation = delete_reservation(
            reservation_id, 
            current_user["id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, details=str(e))
    
    if reservation is None:
        return HTTPException(status_code=404, details="Reservation not found")
    return {"status": "ok"}

@router.get("/active")
def get_active_reservation_endpoint():
    now = datetime.now()
    reservation = get_active_reservation(now)

    if reservation is None:
        return {
            "active": False,
            "reservation": None
        }

    remaining_seconds = int(
        remaining_time(reservation["id"]).total_seconds()
    )

    user_name = get_user_by_id(reservation["user_id"])

    return {
        "active": True,
        "reservation": {
            "id": reservation["id"],
            "user_name": user_name,
            "end_time": reservation["end_time"].isoformat(),
            "seconds_remaining": max(0, remaining_seconds)
        }
    }

# @router.post("/{id}/start-early")
# def start_reservation_early_endpoint(reservation_id: int, current_user = Depends(get_current_user)):
#     try:
#          reservation = start_reservation_early(
#             reservation_id, 
#             current_user["id"]
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, details=str(e))
    
#     if reservation is None:
#         return HTTPException(status_code=404, details="Reservation not found")
#     return reservation

# @router.post("/{id}/extend")
# def extend_reservation_endpoint(reservation_id: int, data: ReservationExtendRequest, current_user = Depends(get_current_user)):
#     try:
#          reservation = extend_reservation(
#             reservation_id, 
#             current_user["id"], 
#             data.minutes
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, details=str(e))
    
#     if reservation is None:
#         return HTTPException(status_code=404, details="Reservation not found")
#     return reservation

# @router.post("/{id}/end-early")
# def end_reservation_early_endpoint(reservation_id: int, current_user = Depends(get_current_user)):
#     try:
#          reservation = end_reservation_early(
#             reservation_id,
#             current_user
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, details=str(e))
    
#     if reservation is None:
#         return HTTPException(status_code=404, details="Reservation not found")
#     return reservation
    
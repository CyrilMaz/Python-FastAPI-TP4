from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, model_validator

router = APIRouter(prefix="/reservations", tags=["Reservations"])

FAKE_USERS_DB: dict[int, dict] = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bilal"},
}

FAKE_ITEMS_DB: dict[int, dict] = {
    1: {"id": 1, "name": "Perceuse", "price_per_day": 5.0},
    2: {"id": 2, "name": "Tondeuse", "price_per_day": 8.0},
}


def user_exists(user_id: int) -> bool:
    return user_id in FAKE_USERS_DB


def item_exists(item_id: int) -> bool:
    return item_id in FAKE_ITEMS_DB


def get_item_price(item_id: int) -> float:
    return FAKE_ITEMS_DB[item_id]["price_per_day"]


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class ReservationBase(BaseModel):
    user_id: int = Field(..., description="Identifiant de l'utilisateur qui réserve")
    item_id: int = Field(..., description="Identifiant de l'objet réservé")
    start_date: date
    end_date: date
    notes: Optional[str] = Field(default=None, max_length=280)

    @model_validator(mode="after")
    def check_dates_coherentes(self) -> "ReservationBase":
        if self.end_date <= self.start_date:
            raise ValueError("end_date doit être strictement postérieure à start_date")
        if self.start_date < date.today():
            raise ValueError("start_date ne peut pas être dans le passé")
        return self


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ReservationStatus] = None
    notes: Optional[str] = Field(default=None, max_length=280)


class Reservation(ReservationBase):
    id: int
    status: ReservationStatus = ReservationStatus.PENDING
    total_price: float = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.now)


reservations_db: dict[int, Reservation] = {}
_next_id = 1


def _generate_id() -> int:
    global _next_id
    new_id = _next_id
    _next_id += 1
    return new_id


@router.post("", response_model=Reservation, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate) -> Reservation:
    if not user_exists(payload.user_id):
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur {payload.user_id} introuvable"
        )

    if not item_exists(payload.item_id):
        raise HTTPException(
            status_code=404,
            detail=f"Objet {payload.item_id} introuvable"
        )

    nb_days = (payload.end_date - payload.start_date).days
    total_price = round(nb_days * get_item_price(payload.item_id), 2)

    reservation = Reservation(
        id=_generate_id(),
        total_price=total_price,
        **payload.model_dump()
    )

    reservations_db[reservation.id] = reservation
    return reservation


@router.get("", response_model=list[Reservation])
def list_reservations(
    user_id: Optional[int] = None,
    item_id: Optional[int] = None,
    status_filter: Optional[ReservationStatus] = Query(default=None, alias="status"),
) -> list[Reservation]:
    results = list(reservations_db.values())

    if user_id is not None:
        results = [r for r in results if r.user_id == user_id]

    if item_id is not None:
        results = [r for r in results if r.item_id == item_id]

    if status_filter is not None:
        results = [r for r in results if r.status == status_filter]

    return results


@router.get("/{reservation_id}", response_model=Reservation)
def get_reservation(reservation_id: int) -> Reservation:
    reservation = reservations_db.get(reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Réservation {reservation_id} introuvable"
        )

    return reservation

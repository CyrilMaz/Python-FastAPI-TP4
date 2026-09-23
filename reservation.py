from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, model_validator

router = APIRouter(prefix="/reservations", tags=["Reservations"])

def user_exists(user_id: int) -> bool:
    """Dépendance injectée depuis main.py."""
    return False


def item_exists(item_id: UUID) -> bool:
    """Dépendance injectée depuis main.py."""
    return False


def get_item_price(item_id: UUID) -> float:
    """Dépendance injectée depuis main.py."""
    raise KeyError(item_id)


def wire_dependencies(
    *,
    user_exists_fn=None,
    item_exists_fn=None,
    item_price_fn=None
) -> None:
    global user_exists, item_exists, get_item_price

    if user_exists_fn is not None:
        user_exists = user_exists_fn

    if item_exists_fn is not None:
        item_exists = item_exists_fn

    if item_price_fn is not None:
        get_item_price = item_price_fn


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class ReservationBase(BaseModel):
    user_id: int = Field(..., description="Identifiant de l'utilisateur qui réserve")
    item_id: UUID = Field(..., description="Identifiant du matériel réservé")
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

    @model_validator(mode="after")
    def check_dates_coherentes(self) -> "ReservationUpdate":
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date doit être strictement postérieure à start_date")

        return self


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


def _overlaps(
    a_start: date,
    a_end: date,
    b_start: date,
    b_end: date
) -> bool:
    return a_start < b_end and b_start < a_end


def _find_conflicting_reservation(
    item_id: UUID,
    start_date: date,
    end_date: date,
    exclude_id: Optional[int] = None
) -> Optional[Reservation]:
    for r in reservations_db.values():
        if r.id == exclude_id:
            continue

        if r.item_id != item_id:
            continue

        if r.status == ReservationStatus.CANCELLED:
            continue

        if _overlaps(start_date, end_date, r.start_date, r.end_date):
            return r

    return None


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

    conflict = _find_conflicting_reservation(
        payload.item_id,
        payload.start_date,
        payload.end_date
    )

    if conflict is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"L'objet {payload.item_id} est déjà réservé du "
                f"{conflict.start_date} au {conflict.end_date} "
                f"(réservation {conflict.id})"
            ),
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
    item_id: Optional[UUID] = None,
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


@router.get("/stats")
def reservation_stats() -> dict:
    all_reservations = list(reservations_db.values())
    total = len(all_reservations)

    by_status = {
        s.value: 0
        for s in ReservationStatus
    }

    for r in all_reservations:
        by_status[r.status.value] += 1

    if total > 0:
        avg_duration = sum(
            (r.end_date - r.start_date).days
            for r in all_reservations
        ) / total

        revenue_confirmed = sum(
            r.total_price
            for r in all_reservations
            if r.status == ReservationStatus.CONFIRMED
        )

        item_counts: dict[UUID, int] = {}

        for r in all_reservations:
            item_counts[r.item_id] = item_counts.get(r.item_id, 0) + 1

        most_reserved_item_id = max(
            item_counts,
            key=item_counts.get
        )

    else:
        avg_duration = 0.0
        revenue_confirmed = 0.0
        most_reserved_item_id = None

    return {
        "total_reservations": total,
        "by_status": by_status,
        "average_duration_days": round(avg_duration, 2),
        "revenue_confirmed": round(revenue_confirmed, 2),
        "most_reserved_item_id": most_reserved_item_id,
    }


@router.get("/{reservation_id}", response_model=Reservation)
def get_reservation(reservation_id: int) -> Reservation:
    reservation = reservations_db.get(reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Réservation {reservation_id} introuvable"
        )

    return reservation


@router.patch("/{reservation_id}", response_model=Reservation)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate
) -> Reservation:
    reservation = reservations_db.get(reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Réservation {reservation_id} introuvable"
        )

    if reservation.status == ReservationStatus.CANCELLED:
        raise HTTPException(
            status_code=403,
            detail="Une réservation annulée ne peut plus être modifiée"
        )

    updates = payload.model_dump(exclude_unset=True)

    new_start = updates.get("start_date", reservation.start_date)
    new_end = updates.get("end_date", reservation.end_date)

    if new_end <= new_start:
        raise HTTPException(
            status_code=400,
            detail="end_date doit être postérieure à start_date"
        )

    if "start_date" in updates or "end_date" in updates:
        conflict = _find_conflicting_reservation(
            reservation.item_id,
            new_start,
            new_end,
            exclude_id=reservation.id
        )

        if conflict is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Conflit avec la réservation {conflict.id} sur ces dates"
            )

    updated = reservation.model_copy(update=updates)
    reservations_db[reservation_id] = updated

    return updated


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int) -> None:
    reservation = reservations_db.get(reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Réservation {reservation_id} introuvable"
        )

    if (
        reservation.status == ReservationStatus.CONFIRMED
        and reservation.start_date <= date.today()
    ):
        raise HTTPException(
            status_code=403,
            detail="Impossible de supprimer une réservation confirmée déjà commencée"
        )

    del reservations_db[reservation_id]
    return None

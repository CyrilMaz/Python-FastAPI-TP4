from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from models import (
    MaterialCondition,
    MaterialCreate,
    MaterialInternal,
    MaterialPage,
    MaterialPublic,
    MaterialSortField,
    MaterialUpdate,
    SortOrder,
)
from store import categories, materials


router = APIRouter(prefix="/materials", tags=["materials"])


def _ensure_category_exists(category_id: UUID) -> None:
    if category_id not in categories:
        raise HTTPException(status_code=404, detail="Category not found")


def _ensure_unique_reference(reference: str, current_id: UUID | None = None) -> None:
    for material_id, material in materials.items():
        if material_id != current_id and material.reference == reference:
            raise HTTPException(status_code=409, detail="A material with this reference already exists")


def _validation_errors(exc: ValidationError) -> list[dict]:
    errors = exc.errors(include_context=False, include_url=False)
    return jsonable_encoder(errors)


@router.post("", response_model=MaterialPublic, status_code=status.HTTP_201_CREATED)
def create_material(payload: MaterialCreate) -> MaterialInternal:
    _ensure_category_exists(payload.category_id)
    _ensure_unique_reference(payload.reference)
    material = MaterialInternal(id=uuid4(), **payload.model_dump())
    materials[material.id] = material
    return material


@router.get("", response_model=MaterialPage)
def list_materials(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    category_id: UUID | None = None,
    condition: MaterialCondition | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: MaterialSortField = MaterialSortField.NAME,
    order: SortOrder = SortOrder.ASC,
) -> dict:
    result = list(materials.values())

    if q is not None:
        needle = q.casefold()
        result = [
            material
            for material in result
            if needle in material.name.casefold()
            or needle in material.reference.casefold()
            or (material.description is not None and needle in material.description.casefold())
        ]
    if category_id is not None:
        result = [material for material in result if material.category_id == category_id]
    if condition is not None:
        result = [material for material in result if material.condition == condition]

    reverse = order == SortOrder.DESC
    result.sort(key=lambda material: getattr(material, sort_by.value), reverse=reverse)

    total = len(result)
    page = result[skip : skip + limit]
    return {"total": total, "skip": skip, "limit": limit, "items": page}


@router.get("/{material_id}", response_model=MaterialPublic)
def get_material(material_id: UUID) -> MaterialInternal:
    material = materials.get(material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.patch("/{material_id}", response_model=MaterialPublic)
def update_material(material_id: UUID, payload: MaterialUpdate) -> MaterialInternal:
    existing = materials.get(material_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Material not found")

    changes = payload.model_dump(exclude_unset=True)
    if "category_id" in changes and changes["category_id"] is not None:
        _ensure_category_exists(changes["category_id"])
    if "reference" in changes and changes["reference"] is not None:
        _ensure_unique_reference(changes["reference"], current_id=material_id)

    updated_data = existing.model_dump()
    updated_data.update(changes)
    try:
        updated = MaterialInternal(**updated_data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=_validation_errors(exc)) from exc

    materials[material_id] = updated
    return updated


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(material_id: UUID) -> Response:
    if material_id not in materials:
        raise HTTPException(status_code=404, detail="Material not found")
    del materials[material_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)

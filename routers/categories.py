from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.models import CategoryCreate, CategoryInternal, CategoryPublic, CategoryUpdate
from app.store import categories, materials


router = APIRouter(prefix="/categories", tags=["categories"])


def _ensure_unique_name(name: str, current_id: UUID | None = None) -> None:
    for category_id, category in categories.items():
        if category_id != current_id and category.name.casefold() == name.casefold():
            raise HTTPException(status_code=409, detail="A category with this name already exists")


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate) -> CategoryInternal:
    _ensure_unique_name(payload.name)
    category = CategoryInternal(id=uuid4(), **payload.model_dump())
    categories[category.id] = category
    return category


@router.get("", response_model=list[CategoryPublic])
def list_categories() -> list[CategoryInternal]:
    return list(categories.values())


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(category_id: UUID) -> CategoryInternal:
    category = categories.get(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: UUID, payload: CategoryUpdate) -> CategoryInternal:
    existing = categories.get(category_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Category not found")

    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and changes["name"] is not None:
        _ensure_unique_name(changes["name"], current_id=category_id)

    updated_data = existing.model_dump()
    updated_data.update(changes)
    try:
        updated = CategoryInternal(**updated_data)
    except ValidationError as exc:
        detail = jsonable_encoder(exc.errors(include_context=False, include_url=False))
        raise HTTPException(status_code=422, detail=detail) from exc
    categories[category_id] = updated
    return updated


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: UUID) -> Response:
    if category_id not in categories:
        raise HTTPException(status_code=404, detail="Category not found")
    if any(material.category_id == category_id for material in materials.values()):
        raise HTTPException(status_code=409, detail="Category is still used by materials")
    del categories[category_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)

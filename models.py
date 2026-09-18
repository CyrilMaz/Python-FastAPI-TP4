from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class MaterialCondition(str, Enum):
    """États métier autorisés pour un matériel."""

    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class MaterialSortField(str, Enum):
    NAME = "name"
    REFERENCE = "reference"
    DAILY_RATE = "daily_rate"
    TOTAL_QUANTITY = "total_quantity"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=300)
    internal_notes: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Évite les noms visuellement vides et les espaces parasites."""
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("category name must contain at least 2 visible characters")
        return normalized


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=300)
    internal_notes: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("category name must contain at least 2 visible characters")
        return normalized


class CategoryInternal(CategoryCreate):
    id: UUID


class CategoryPublic(BaseModel):
    """Représentation publique : les notes de gestion internes sont masquées."""

    id: UUID
    name: str
    description: str | None = None


class MaterialCreate(BaseModel):
    reference: str = Field(min_length=3, max_length=30, pattern=r"^[A-Z0-9-]+$")
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    category_id: UUID
    condition: MaterialCondition = MaterialCondition.GOOD
    total_quantity: int = Field(ge=0, le=10_000)
    available_quantity: int = Field(ge=0, le=10_000)
    daily_rate: Decimal = Field(ge=0, max_digits=10, decimal_places=2)

    @field_validator("reference", mode="before")
    @classmethod
    def normalize_reference(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("material name must contain at least 2 visible characters")
        return normalized

    @model_validator(mode="after")
    def validate_quantities(self) -> "MaterialCreate":
        if self.available_quantity > self.total_quantity:
            raise ValueError("available_quantity cannot exceed total_quantity")
        return self


class MaterialUpdate(BaseModel):
    reference: str | None = Field(default=None, min_length=3, max_length=30, pattern=r"^[A-Z0-9-]+$")
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    category_id: UUID | None = None
    condition: MaterialCondition | None = None
    total_quantity: int | None = Field(default=None, ge=0, le=10_000)
    available_quantity: int | None = Field(default=None, ge=0, le=10_000)
    daily_rate: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)

    @field_validator("reference", mode="before")
    @classmethod
    def normalize_reference(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("material name must contain at least 2 visible characters")
        return normalized

    @model_validator(mode="after")
    def validate_quantities_when_both_are_provided(self) -> "MaterialUpdate":
        if (
            self.total_quantity is not None
            and self.available_quantity is not None
            and self.available_quantity > self.total_quantity
        ):
            raise ValueError("available_quantity cannot exceed total_quantity")
        return self


class MaterialInternal(MaterialCreate):
    id: UUID


class MaterialPublic(BaseModel):
    id: UUID
    reference: str
    name: str
    description: str | None = None
    category_id: UUID
    condition: MaterialCondition
    total_quantity: int
    available_quantity: int
    daily_rate: Decimal


class MaterialPage(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[MaterialPublic]

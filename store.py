from uuid import UUID

from app.models import CategoryInternal, MaterialInternal


categories: dict[UUID, CategoryInternal] = {}
materials: dict[UUID, MaterialInternal] = {}


def reset_store() -> None:
    """Utilisé par les tests pour isoler les scénarios."""
    categories.clear()
    materials.clear()

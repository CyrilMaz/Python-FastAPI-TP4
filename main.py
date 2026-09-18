from fastapi import FastAPI

from reservation import router as reservation_router
from routers.categories import router as categories_router
from routers.materials import router as materials_router


app = FastAPI(
    title="Catalogue de matériel et réservations",
    version="1.0.0",
    description="API de catalogue de matériel et de gestion des réservations.",
)

app.include_router(reservation_router)
app.include_router(categories_router)
app.include_router(materials_router)


@app.get("/")
def root():
    return {
        "message": "Démo de la partie Réservations. Ouvre /docs pour tester les routes."
    }


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}

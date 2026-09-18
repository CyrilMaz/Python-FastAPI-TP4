from fastapi import FastAPI

from app.routers.categories import router as categories_router
from app.routers.materials import router as materials_router


app = FastAPI(
    title="Catalogue de matériel",
    version="1.0.0",
    description="Partie catalogue : ressources Category et Material.",
)

app.include_router(categories_router)
app.include_router(materials_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}

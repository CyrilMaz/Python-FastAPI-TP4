from fastapi import FastAPI

from reservation import router as reservation_router

app = FastAPI(title="Démo — Partie 3 (Réservations)")

app.include_router(reservation_router)


@app.get("/")
def root():
    return {
        "message": "Démo de la partie Réservations. Ouvre /docs pour tester les routes."
    }

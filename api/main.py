# api/main.py
"""
Point d'entrée de l'API Job Market.
Lance avec : uvicorn api.main:app --reload
"""

from fastapi import FastAPI
from api.routes import jobs, recommend

app = FastAPI(
    title       = "Job Market API",
    description = "API de recherche et recommandation d'offres d'emploi",
    version     = "1.0.0",
)

# Enregistrer les routes
app.include_router(jobs.router)
app.include_router(recommend.router)

@app.get("/")
def racine():
    return {
        "message": "Job Market API",
        "version": "1.0.0",
        "endpoints": {
            "recherche":      "/jobs?q=data+engineer",
            "detail":         "/jobs/{id}",
            "recommandations": "/recommend/{id}",
            "documentation":  "/docs",
        }
    }

@app.get("/health")
def health():
    """Endpoint de santé — vérifie que l'API répond."""
    return {"status": "ok"}


'''
Lancer uvicorn :  uvicorn api.main:app --reload

'''

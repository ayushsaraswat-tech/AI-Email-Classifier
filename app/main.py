from fastapi import FastAPI
from app.routes import email_routes
from app.database import engine, Base
from app.models import email_model

app = FastAPI(title="AI Email Assistant")

Base.metadata.create_all(bind=engine)

app.include_router(email_routes.router)


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
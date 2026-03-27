from fastapi import FastAPI
from app.routes import email_routes
from app.database import engine, Base
from app.models import email_model
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="AI Email Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(email_routes.router)


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

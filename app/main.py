from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import email_model, user_model

app = FastAPI(title="AI Email Assistant")

# ✅ CREATE TABLES
Base.metadata.create_all(bind=engine)

# ✅ IMPORT AFTER app creation
from app.routes import auth_routes
from app.routes import email_routes

# ✅ INCLUDE ROUTERS
app.include_router(auth_routes.router)
app.include_router(email_routes.router)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import email_model, user_model
from fastapi.security import HTTPBearer

security = HTTPBearer()

app = FastAPI(
    title="AI Email Assistant",
    swagger_ui_parameters={"persistAuthorization": True}
)


# ✅ CREATE TABLES
Base.metadata.create_all(bind=engine)

# ✅ CORS MUST BE ADDED HERE (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175"],  # 👈 VERY IMPORTANT
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ IMPORT ROUTES AFTER app creation
from app.routes import auth_routes, email_routes

app.include_router(auth_routes.router)
app.include_router(email_routes.router)
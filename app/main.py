from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

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

with engine.begin() as connection:
    existing_columns = {
        column["name"] for column in inspect(connection).get_columns("user_emails")
    }
    oauth_columns = {
        "auth_type": "VARCHAR DEFAULT 'imap'",
        "access_token": "TEXT",
        "refresh_token": "TEXT",
        "token_uri": "VARCHAR",
        "scopes": "TEXT",
    }
    for column_name, column_type in oauth_columns.items():
        if column_name not in existing_columns:
            connection.execute(text(f"ALTER TABLE user_emails ADD COLUMN {column_name} {column_type}"))

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

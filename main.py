from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

# Database utilities are pre-configured in this environment
# They expose: db (Motor/Mongo client), create_document, get_documents
try:
    from database import db, create_document, get_documents  # type: ignore
except Exception as e:
    db = None  # fallback to allow app to start even if import fails
    def create_document(collection_name: str, data: Dict[str, Any]):
        raise RuntimeError("Database utilities not available: " + str(e))
    def get_documents(collection_name: str, filter_dict: Dict[str, Any] | None = None, limit: int = 50):
        raise RuntimeError("Database utilities not available: " + str(e))

app = FastAPI(title="POD API", version="1.0.0")

# CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None


class ProfileCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    full_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    disability_type: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None


class ProfileResponse(BaseModel):
    success: bool
    id: Optional[str] = None
    message: str


@app.get("/")
async def root():
    return {"message": "POD API is running"}


@app.get("/test")
async def test_connection():
    info: Dict[str, Any] = {
        "backend": "fastapi",
        "database": "mongodb",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    try:
        # Try to read some metadata from the db
        database_url = getattr(db, "client", None).address if db else None  # type: ignore
        info.update({
            "database_url": str(database_url) if database_url else "connected",
            "database_name": getattr(db, "name", "unknown") if db else "unknown",
            "connection_status": "ok" if db else "not_configured",
        })
        # List collections if possible
        try:
            collections = []
            if db:
                collections = await db.list_collection_names()  # type: ignore
            info["collections"] = collections
        except Exception:
            info["collections"] = []
    except Exception as e:
        info["connection_status"] = f"error: {e}"
    return info


@app.post("/auth/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    # Basic placeholder auth flow: verify user exists, otherwise create a minimal record.
    # In production, replace with proper OAuth2/password hashing.
    try:
        users = await get_documents("user", {"email": payload.email}, limit=1)  # type: ignore
        if users:
            token = "demo-token"
            return LoginResponse(success=True, message="Login successful", token=token)
        # Auto-register minimal user document
        user_doc = {
            "email": payload.email,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        await create_document("user", user_doc)  # type: ignore
        token = "demo-token"
        return LoginResponse(success=True, message="Account created and logged in", token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/profile/create", response_model=ProfileResponse)
async def create_profile(payload: ProfileCreateRequest):
    # Simple uniqueness check on username
    try:
        existing = await get_documents("profile", {"username": payload.username}, limit=1)  # type: ignore
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        doc = payload.dict()
        doc["created_at"] = datetime.utcnow().isoformat() + "Z"
        result = await create_document("profile", doc)  # type: ignore
        # result may be an inserted id or document
        inserted_id = None
        if isinstance(result, dict):
            inserted_id = str(result.get("_id")) if result.get("_id") else None
        return ProfileResponse(success=True, id=inserted_id, message="Profile created")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

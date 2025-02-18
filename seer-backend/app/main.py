from fastapi import FastAPI
from app.routes import auth, admin
from app.database.database import SessionLocal
from app.database.seed import seed_roles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import iam, threats


app = FastAPI()

# ✅ Allow CORS for Next.js frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # ✅ Allow all headers
)

app.include_router(auth.router, prefix="")
app.include_router(admin.router, prefix="")

app.include_router(iam.router)
app.include_router(threats.router)


@app.get("/")
def home():
    return {"message": "SEER Backend is running!"}

# ✅ Run role seeding on startup
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()

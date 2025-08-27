from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, root_path="/api")

# ---------- Middleware ---------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Routing ------------ #
# app.include_router(users.router)
# app.include_router(auth.router)


@app.get("/")
def home():
    # health check
    return {"msg": "ok"}

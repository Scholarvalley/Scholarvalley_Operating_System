from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import auth, applicants, dashboard, documents, eligibility, messages, ml, payments, tasks, uploads
from app.core.config import get_settings


settings = get_settings()


def _internal_error_detail(exc: Exception) -> str:
    """Return a safe message for 500 responses."""
    msg = str(exc).strip() or type(exc).__name__
    if "connection" in msg.lower() or "connect" in msg.lower():
        return "Database connection failed. Check that PostgreSQL is running and DATABASE_URL is correct."
    if "password" in msg.lower() or "auth" in msg.lower():
        return "Database authentication failed. Check DATABASE_URL credentials."
    return msg[:200]

# Project root (parent of app/)
ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "static"

app = FastAPI(
    title="ScholarValley Operating System API",
    version="0.1.0",
)

allowed_origins = ["*"]
if settings.frontend_origin:
    allowed_origins = [str(settings.frontend_origin)]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def static_cache_control(request: Request, call_next):
    """Ensure static assets (e.g. logo.png) can be updated without hard refresh."""
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers.setdefault("Cache-Control", "no-cache")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return JSON for unhandled exceptions (not HTTPException) so the frontend never sees HTML."""
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    detail = _internal_error_detail(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": detail},
    )

# Static assets (CSS, JS)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok"}


# Frontend – Scholarvalley (every page from archive)
def _send_static_html(name: str):
    path = STATIC_DIR / f"{name}.html"
    if path.exists():
        return FileResponse(path)
    return None


@app.get("/", include_in_schema=False)
async def frontend_index():
    return _send_static_html("index") or {"message": "Scholarvalley API", "docs": "/docs"}


@app.get("/about", include_in_schema=False)
async def frontend_about():
    return _send_static_html("about") or FileResponse(STATIC_DIR / "index.html")


@app.get("/services", include_in_schema=False)
async def frontend_services():
    return _send_static_html("services") or FileResponse(STATIC_DIR / "index.html")


@app.get("/contact", include_in_schema=False)
async def frontend_contact():
    return _send_static_html("contact") or FileResponse(STATIC_DIR / "index.html")


@app.get("/register", include_in_schema=False)
async def frontend_register():
    return _send_static_html("register") or FileResponse(STATIC_DIR / "index.html")


@app.get("/login", include_in_schema=False)
async def frontend_login():
    return _send_static_html("login") or FileResponse(STATIC_DIR / "index.html")


@app.get("/dashboard", include_in_schema=False)
async def frontend_dashboard():
    return _send_static_html("dashboard") or FileResponse(STATIC_DIR / "index.html")


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(applicants.router, prefix="/api/applicants", tags=["applicants"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(eligibility.router, prefix="/api/eligibility", tags=["eligibility"])
app.include_router(ml.router, prefix="/api/ml", tags=["ml"])


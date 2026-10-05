"""DevLens FastAPI Application Entrypoint."""

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1.router import api_v1_router
from .config import settings
from .database.session import init_db
from .logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks: initialize database on startup."""
    logger.info("DevLens backend starting up...")
    init_db()
    yield
    logger.info("DevLens backend shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "DevLens: Production-Grade Code Intelligence, Debugging & Learning Platform. "
        "Combines deterministic AST static analysis with educational AI synthesis. "
        "Designed with security best practices and continuously tested for common vulnerabilities."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware with explicit whitelist
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Injects defensive HTTP security headers into every response."""
    response: Response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Sanitizes unhandled internal exceptions to prevent information disclosure."""
    ref_id = str(uuid.uuid4())[:8]
    logger.error(f"[Ref: {ref_id}] Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Something went wrong while processing your request.",
            "reference_id": ref_id,
        },
    )


# Include API Routers
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "security_statement": "Designed with security best practices and continuously tested for common vulnerabilities.",
    }

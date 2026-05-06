from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.errors import AppError
from app.routes.analyses import router as analyses_router
from app.services.openrouter_client import request_openrouter_ping

app = FastAPI(
    title="Analise de Curriculo com IA",
    version="1.0.0",
    description="API para comparar curriculos PDF/DOCX com descricoes de vaga usando OpenRouter.",
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "internal_error",
                "message": "Ocorreu um erro inesperado ao processar a analise.",
                "details": {"type": exc.__class__.__name__},
            },
        },
    )


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(settings.static_dir / "index.html")


@app.get("/api/health")
async def health() -> dict:
    return {"success": True, "data": {"status": "ok", "model": settings.openrouter_model}}


@app.get("/api/ready")
async def ready() -> dict:
    return {
        "success": True,
        "data": {
            "status": "ready" if settings.openrouter_api_key else "missing_api_key",
            "has_openrouter_api_key": bool(settings.openrouter_api_key),
        },
    }


@app.get("/api/openrouter-test")
async def openrouter_test() -> dict:
    content = await request_openrouter_ping()
    return {
        "success": True,
        "data": {
            "status": "ok",
            "model": settings.openrouter_model,
            "response": content,
        },
    }


app.include_router(analyses_router)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

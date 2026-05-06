from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import settings
from app.core.errors import AppError
from app.services.document_extractor import extract_resume_text
from app.services.openrouter_client import request_resume_analysis

router = APIRouter(prefix="/api", tags=["analyses"])


@router.post("/analyses")
async def create_analysis(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
) -> dict:
    filename = resume.filename or ""
    extension = Path(filename).suffix.lower()
    cleaned_job_description = normalize_text(job_description)

    if extension not in settings.allowed_extensions:
        raise AppError(
            status_code=415,
            code="unsupported_file_type",
            message="Envie um arquivo .pdf ou .docx.",
            details={"allowed_extensions": sorted(settings.allowed_extensions)},
        )

    if len(cleaned_job_description) < settings.min_job_description_chars:
        raise AppError(
            status_code=422,
            code="invalid_job_description",
            message="Cole uma descricao da vaga com detalhes suficientes para analise.",
            details={"min_characters": settings.min_job_description_chars},
        )

    if len(cleaned_job_description) > settings.max_job_description_chars:
        raise AppError(
            status_code=413,
            code="job_description_too_long",
            message="A descricao da vaga excede o limite permitido.",
            details={"max_characters": settings.max_job_description_chars},
        )

    file_bytes = await resume.read()
    if not file_bytes:
        raise AppError(status_code=422, code="empty_file", message="O arquivo enviado esta vazio.")

    if len(file_bytes) > settings.max_upload_bytes:
        raise AppError(
            status_code=413,
            code="file_too_large",
            message="O arquivo excede o limite permitido.",
            details={"max_bytes": settings.max_upload_bytes},
        )

    resume_text = extract_resume_text(file_bytes=file_bytes, extension=extension)
    if not resume_text.strip():
        raise AppError(
            status_code=422,
            code="unreadable_file",
            message="Nao foi possivel extrair texto do arquivo. Verifique se o PDF nao e apenas imagem digitalizada.",
        )

    analysis = await request_resume_analysis(
        resume_text=resume_text[: settings.max_resume_chars],
        job_description=cleaned_job_description,
    )

    return {
        "success": True,
        "data": {
            "analysis": analysis,
            "model": settings.openrouter_model,
            "filename": filename,
            "resume_characters": len(resume_text),
            "resume_truncated": len(resume_text) > settings.max_resume_chars,
        },
    }


def normalize_text(value: str) -> str:
    cleaned = "".join(ch for ch in value if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    return cleaned.strip()

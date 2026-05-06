import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class Settings:
    base_dir: Path = BASE_DIR
    static_dir: Path = BASE_DIR / "static"

    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    openrouter_app_url: str = os.getenv("OPENROUTER_APP_URL", "http://localhost:8000")
    openrouter_app_name: str = os.getenv("OPENROUTER_APP_NAME", "Analise de Curriculo com IA")
    openrouter_max_completion_tokens: int = int(os.getenv("OPENROUTER_MAX_COMPLETION_TOKENS", "4096"))

    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(8 * 1024 * 1024)))
    max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "40"))
    max_resume_chars: int = int(os.getenv("MAX_RESUME_CHARS", "40000"))
    max_job_description_chars: int = int(os.getenv("MAX_JOB_DESCRIPTION_CHARS", "20000"))
    min_job_description_chars: int = int(os.getenv("MIN_JOB_DESCRIPTION_CHARS", "20"))
    allowed_extensions: set[str] = {".pdf", ".docx"}

    cors_origins: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


settings = Settings()

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'college.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
    LOCAL_MODEL_BASE_URL = os.environ.get("LOCAL_MODEL_BASE_URL", "http://localhost:12434")
    LOCAL_MODEL_NAME = os.environ.get("LOCAL_MODEL_NAME", "ai/gemma3-qat:latest")

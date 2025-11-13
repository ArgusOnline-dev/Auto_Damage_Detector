"""Core configuration settings for the FastAPI application."""
import os
from pathlib import Path
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Auto Damage Detector API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png"]
    UPLOAD_DIR: Path = Path("data/uploads")
    TEMP_DIR: Path = Path("data/temp")

    # ML Model Settings
    # Stage 1: Parts-only detector (detects car parts without damage types)
    PART_MODEL_PATH: Path = Path(os.getenv("PART_MODEL_PATH", "models/yolov8n_part_detector.pt"))
    # Stage 2: Damage-only detector (detects damage types: dent, scratch, intact, etc.)
    DAMAGE_MODEL_PATH: Path = Path(os.getenv("DAMAGE_MODEL_PATH", "models/yolov8n_damage.pt"))
    ML_DEVICE: str = os.getenv("ML_DEVICE", "cpu")
    PART_CONF_THRESHOLD: float = float(os.getenv("PART_CONF_THRESHOLD", "0.25"))
    DAMAGE_CONF_THRESHOLD: float = float(os.getenv("DAMAGE_CONF_THRESHOLD", "0.25"))
    DAMAGE_MATCH_MIN_IOU: float = float(os.getenv("DAMAGE_MATCH_MIN_IOU", "0.1"))
    COST_RULES_PATH: Path = Path(os.getenv("COST_RULES_PATH", "data/auto_damage_repair_costs_MASTER.csv"))
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # Allow all origins for now
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create directories if they don't exist
settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)


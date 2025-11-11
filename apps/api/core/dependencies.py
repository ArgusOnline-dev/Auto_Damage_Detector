"""Dependency injection for FastAPI."""
from typing import Generator
from fastapi import Depends
from apps.api.core.config import settings


def get_settings():
    """Dependency to get application settings."""
    return settings


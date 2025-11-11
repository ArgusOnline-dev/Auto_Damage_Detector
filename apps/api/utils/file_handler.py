"""File upload handling utilities."""
import uuid
import io
from pathlib import Path
from typing import List
from fastapi import UploadFile
from PIL import Image
from apps.api.core.config import settings
from apps.api.core.exceptions import FileValidationError, FileNotFoundError


class FileHandler:
    """Handles file uploads, validation, and storage."""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.temp_dir = settings.TEMP_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self._file_registry = {}  # In-memory registry: file_id -> file_path
    
    def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            raise FileValidationError(
                f"Invalid file type. Only {', '.join(self.allowed_extensions)} allowed"
            )
        
        # Check file size (we'll check after reading)
        if file.size and file.size > self.max_file_size:
            raise FileValidationError(
                f"File size exceeds limit of {self.max_file_size / (1024*1024):.1f}MB"
            )
    
    async def save_file(self, file: UploadFile) -> str:
        """Save uploaded file and return file ID."""
        # Validate file
        self.validate_file(file)
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > self.max_file_size:
            raise FileValidationError(
                f"File size exceeds limit of {self.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Check if file is empty
        if len(content) == 0:
            raise FileValidationError("File is empty")
        
        # Validate image format
        try:
            image = Image.open(io.BytesIO(content))
            image.verify()  # Verify it's a valid image
        except Exception as e:
            raise FileValidationError(f"Invalid image file: {str(e)}")
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix.lower()
        file_path = self.temp_dir / f"{file_id}{file_ext}"
        
        # Save file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Register file
        self._file_registry[file_id] = str(file_path)
        
        return file_id
    
    async def save_files(self, files: List[UploadFile]) -> List[str]:
        """Save multiple files and return list of file IDs."""
        file_ids = []
        for file in files:
            file_id = await self.save_file(file)
            file_ids.append(file_id)
        return file_ids
    
    def get_file_path(self, file_id: str) -> Path:
        """Get file path by file ID."""
        if file_id not in self._file_registry:
            raise FileNotFoundError(file_id)
        return Path(self._file_registry[file_id])
    
    def file_exists(self, file_id: str) -> bool:
        """Check if file exists."""
        if file_id not in self._file_registry:
            return False
        file_path = Path(self._file_registry[file_id])
        return file_path.exists()
    
    def cleanup_file(self, file_id: str) -> None:
        """Remove file from storage and registry."""
        if file_id in self._file_registry:
            file_path = Path(self._file_registry[file_id])
            if file_path.exists():
                file_path.unlink()
            del self._file_registry[file_id]
    
    def cleanup_files(self, file_ids: List[str]) -> None:
        """Remove multiple files."""
        for file_id in file_ids:
            try:
                self.cleanup_file(file_id)
            except Exception:
                pass  # Ignore errors during cleanup


# Global file handler instance
file_handler = FileHandler()


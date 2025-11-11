"""Custom exceptions for the API."""
from fastapi import HTTPException, status


class AutoDamageException(HTTPException):
    """Base exception for Auto Damage Detector API."""
    pass


class FileValidationError(AutoDamageException):
    """Exception raised when file validation fails."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class FileNotFoundError(AutoDamageException):
    """Exception raised when file is not found."""
    def __init__(self, file_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {file_id}"
        )


class InferenceError(AutoDamageException):
    """Exception raised when inference fails."""
    def __init__(self, detail: str = "Inference failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class CostEstimationError(AutoDamageException):
    """Exception raised when cost estimation fails."""
    def __init__(self, detail: str = "Cost estimation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ReportGenerationError(AutoDamageException):
    """Exception raised when report generation fails."""
    def __init__(self, detail: str = "Report generation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


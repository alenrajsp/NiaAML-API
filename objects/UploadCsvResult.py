from pydantic import BaseModel


class UploadCsvResult(BaseModel):
    """JSON model for return of upload CSV method"""
    file_id: str
    result: str

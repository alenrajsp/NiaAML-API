from pydantic import BaseModel


class UploadCsvResult(BaseModel):
    """JSON model for return of upload CSV method"""
    data_id: str
    result: str

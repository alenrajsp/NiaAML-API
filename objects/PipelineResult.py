from pydantic import BaseModel


class PipelineResult(BaseModel):
    """JSON model for return of running pipeline method"""
    file_id: str
    result: str

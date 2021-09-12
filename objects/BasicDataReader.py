from collections import Iterable
from typing import Any, Optional
from pydantic import BaseModel


class WebBasicDataReader(BaseModel):
    x: Iterable[Any]
    y: Optional[Iterable[Any]]

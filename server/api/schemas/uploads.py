from datetime import datetime
from typing import List, Optional, Set

from pydantic import BaseModel


class Upload(BaseModel):
    id: int
    file_name: str
    number_of_rows: int
    created_at: datetime

    class Config:
        orm_mode = True

class UploadCreate(BaseModel):
    file_name: str
    number_of_rows: int
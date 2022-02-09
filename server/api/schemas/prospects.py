from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from pydantic.networks import EmailStr

from fastapi import Form, File, UploadFile


class Prospect(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProspectCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class ProspectResponse(BaseModel):
    """One page of prospects"""

    prospects: List[Prospect]
    size: int
    total: int


class ProspectFilesUpload(BaseModel):
    file: UploadFile
    email_index: int
    first_name_index: Optional[int]
    last_name_index: Optional[int]
    force: bool
    has_headers: bool

    @classmethod
    def to_form(
        cls,
        file: UploadFile = File(...),
        email_index: int = Form(...),
        first_name_index: Optional[int] = Form(None),
        last_name_index: Optional[int] = Form(None),
        force: bool = Form(...),
        has_headers: bool = Form(...),
    ):
        return cls(
            file=file,
            email_index=email_index,
            first_name_index=first_name_index,
            last_name_index=last_name_index,
            force=force,
            has_headers=has_headers,
        )


class ProspectFilesResponse(BaseModel):
    response: int

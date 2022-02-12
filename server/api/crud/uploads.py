from typing import List, Set, Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import Upload
from api.core.constants import DEFAULT_PAGE_SIZE, DEFAULT_PAGE, MIN_PAGE, MAX_PAGE_SIZE
from datetime import datetime


class UploadCrud: 
    @classmethod
    def create_upload_data(
        cls, db: Session, user_id: int, data: schemas.UploadCreate
    ) -> Upload:
        """Create upload data"""
        upload = Upload(**data, user_id=user_id)
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload
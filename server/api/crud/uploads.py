from typing import List, Set, Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import Upload, Prospect
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

    @classmethod
    def get_upload_status(
        cls,
        upload_id: int,
        db: Session,
        user_id: int,
    ):
        """Get Upload Status"""
        status = db.query(Prospect).filter(Prospect.upload_id == upload_id).count()
        return status

    @classmethod
    def get_file_row_count(cls, upload_id: int, db: Session, user_id: int):
        """Get total number of rows in uploaded file"""
        total = db.query(Upload).filter(Upload.id == upload_id).first().number_of_rows
        return total

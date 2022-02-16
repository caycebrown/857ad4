from black import io
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Depends, Header
from sqlalchemy import schema, true
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from api.crud import ProspectCrud, UploadCrud
from api.dependencies.db import get_db
import csv

router = APIRouter(prefix="/api", tags=["prospects"])


@router.get("/prospects", response_model=schemas.ProspectResponse)
def get_prospects_page(
    current_user: schemas.User = Depends(get_current_user),
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
):
    """Get a single page of prospects"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    prospects = ProspectCrud.get_users_prospects(db, current_user.id, page, page_size)
    total = ProspectCrud.get_user_prospects_total(db, current_user.id)
    return {"prospects": prospects, "size": len(prospects), "total": total}


@router.post("/prospects_files/import")
def post_prospects_file(
    *,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    content_type=Header("multipart/form-data"),
    form_data: schemas.ProspectFilesUpload = Depends(
        schemas.ProspectFilesUpload.to_form
    ),
    background_task: BackgroundTasks,
):
    """Upload csv file + file mapping data"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    def upload_data():
        wrapper = io.TextIOWrapper(form_data.file.file._file, encoding="UTF-8")
        reader = csv.reader(wrapper, delimiter=",")
        csv_data = list(reader)

        with open(
            "./uploaded_files/" + form_data.file.filename, "w", newline=""
        ) as saved_file:
            writer = csv.writer(saved_file)
            writer.writerows(csv_data)
            saved_file.close()

        upload_file_data = UploadCrud.create_upload_data(
            db,
            current_user.id,
            {"file_name": form_data.file.filename, "number_of_rows": len(csv_data)},
        )

        current_prospects = ProspectCrud.get_prospect_emails(db, current_user.id)

        if form_data.has_headers:
            next(reader)

        for row in csv_data:
            data = {
                "email": row[form_data.email_index],
                "first_name": row[form_data.first_name_index],
                "last_name": row[form_data.last_name_index],
                "upload_id": upload_file_data.id,
            }

            if row[form_data.email_index] in current_prospects and form_data.force:
                update_prospect = ProspectCrud.update_existing_prospect(
                    db, current_user.id, data
                )

            else:
                add_prospect = ProspectCrud.create_prospect(db, current_user.id, data)

    background_task.add_task(upload_data)

    return {"message": "upload started", "status": status.HTTP_200_OK}


@router.get("/prospects_files/{upload_id}/progress}")
def upload_progress(
    upload_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gets the current number of prospects uploaded from a specified file"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    progress = UploadCrud.get_upload_status(upload_id, db, current_user.id)
    total = UploadCrud.get_file_row_count(upload_id, db, current_user.id)
    return {"total uploaded": progress, "total in file": total}

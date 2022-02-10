from black import io
from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy import true
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from api.crud import ProspectCrud
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
async def post_prospects_file(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    content_type=Header("multipart/form-data"),
    form_data: schemas.ProspectFilesUpload = Depends(
        schemas.ProspectFilesUpload.to_form
    ),
):
    """Upload csv file + file mapping data"""

    wrapper = io.TextIOWrapper(form_data.file.file._file, encoding="UTF-8")
    reader = csv.reader(wrapper, delimiter=",")
    current_prospects = ProspectCrud.get_prospect_emails(db, 1)

    if form_data.has_headers:
        next(reader)

    for row in reader:
        data = {
            "email": row[form_data.email_index],
            "first_name": row[form_data.first_name_index],
            "last_name": row[form_data.last_name_index],
        }

        if row[form_data.email_index] in current_prospects and form_data.force:
            """new prospect update method will go here"""
        else:
            add_prospect = ProspectCrud.create_prospect(db, 1, data)
    return {"data": "test"}

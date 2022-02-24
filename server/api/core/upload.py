from black import io
from sqlalchemy import null
from api.crud import ProspectCrud, UploadCrud
from api.models import Prospect
import csv
from email_validator import validate_email, EmailNotValidError


def upload_data(form_data, db, current_user):
    wrapper = io.TextIOWrapper(form_data.file.file._file, encoding="UTF-8")
    reader = csv.reader(wrapper, delimiter=",")
    csv_data = list(reader)

    with open(
        "./uploaded_files/" + form_data.file.filename + "{current_user.id}",
        "w",
        newline="",
    ) as saved_file:
        writer = csv.writer(saved_file)
        writer.writerows(csv_data)
        saved_file.close()

    upload_file_data = UploadCrud.create_upload_data(
        db,
        current_user.id,
        {"file_name": form_data.file.filename, "number_of_rows": len(csv_data)},
    )

    if form_data.has_headers:
        next(reader)

    for row in csv_data:

        try:
            first_name = row[form_data.first_name_index]
        except IndexError:
            first_name = ""
        try:
            last_name = row[form_data.last_name_index]
        except IndexError:
            last_name = ""

        data = {
            "email": row[form_data.email_index],
            "first_name": first_name,
            "last_name": last_name,
            "upload_id": upload_file_data.id,
        }

        exists = (
            db.query(Prospect)
            .filter(
                Prospect.email == row[form_data.email_index],
                Prospect.user_id == current_user.id,
            )
            .first()
        )

        try:
            valid_email = validate_email(row[form_data.email_index])
        except EmailNotValidError as error:
            continue

        if not valid_email.email:
            continue
        elif exists:
            if form_data.force:
                update_prospect = ProspectCrud.update_existing_prospect(
                    db, current_user.id, data
                )
        else:
            add_prospect = ProspectCrud.create_prospect(db, current_user.id, data)

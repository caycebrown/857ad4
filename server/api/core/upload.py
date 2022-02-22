from pickle import FALSE
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
        "./uploaded_files/" + form_data.file.filename + "1", "w", newline=""
    ) as saved_file:
        writer = csv.writer(saved_file)
        writer.writerows(csv_data)
        saved_file.close()

    upload_file_data = UploadCrud.create_upload_data(
        db,
        1,
        {"file_name": form_data.file.filename, "number_of_rows": len(csv_data)},
    )

    if form_data.has_headers:
        next(reader)

    for row in csv_data:
        data = {
            "email": row[form_data.email_index],
            "first_name": row[form_data.first_name_index]
            if row[form_data.first_name_index]
            else null,
            "last_name": row[form_data.last_name_index]
            if row[form_data.last_name_index]
            else null,
            "upload_id": upload_file_data.id,
        }

        exists = (
            db.query(Prospect)
            .filter(Prospect.email == row[form_data.email_index])
            .first()
        )

        try:
            valid_email = validate_email(row[form_data.email_index])
        except EmailNotValidError as error:
            print(str(error))

        if valid_email.email == FALSE:
            return
        elif exists and form_data.force:
            update_prospect = ProspectCrud.update_existing_prospect(db, 1, data)
        elif exists:
            """Skip Propsect - Do Nothing"""
        else:
            add_prospect = ProspectCrud.create_prospect(db, 1, data)

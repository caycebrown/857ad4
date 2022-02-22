from black import io
from api.crud import ProspectCrud, UploadCrud
import csv


def upload_data(form_data, db, current_user):
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

 
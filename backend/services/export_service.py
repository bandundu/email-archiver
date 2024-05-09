# Services are used to interact with the database, perform business logic and other necesarry core functions. They are to be imported into the routes. Services should not use FastAPI's Request and Response classes. They should only return data to the routes. The routes will then use this data to return a response to the client.

from models.database import get_db
from models.models import Email
import logging
import zipfile
import io

logger = logging.getLogger(__name__)

def export_all_emails():
    db = next(get_db())
    emails = db.query(Email).all()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for email in emails:
            email_id = email.id
            email_data = email.body  # Assuming the body column contains the raw email data
            zip_file.writestr(f"email_{email_id}.eml", email_data)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
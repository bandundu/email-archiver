# Routes are responsible only responsible for handling requests, validating input, and returning responses. They should not contain any business logic. The business logic should be implemented in services.

# exports.py is a file that defines the API endpoints for exporting email data. The export_email endpoint exports a single email with the specified email_id as an EML file. The export_all_emails endpoint exports all emails as a ZIP file. The export_search_results endpoint exports search results based on the specified query as a ZIP file.
import logging

from fastapi import APIRouter, Response
import services.email_service as email_service
from api.schemas.schemas import SearchQuery
from config.config import config

router = APIRouter()


@router.get("/export_email/{email_id}")
def export_email(email_id: int):
    logging.debug(f"Received request to export email {email_id}")
    email_data = email_service.export_email(email_id)

    if email_data:
        logging.debug(f"Exported email {email_id}")
        return Response(
            content=email_data,
            media_type="message/rfc822",
            headers={
                "Content-Disposition": f"attachment; filename=email_{email_id}.eml"
            },
        )
    else:
        logging.error(f"Email {email_id} not found")
        return {"error": "Email not found"}
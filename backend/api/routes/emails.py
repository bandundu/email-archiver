import logging
from fastapi import APIRouter
from api.schemas.schemas import SearchQuery
import services.email_service as email_service
import services.search_service as search_service

# Create a new FastAPI router
router = APIRouter()


@router.get("/emails")
def get_emails():
    logging.debug("Received request to get emails")
    return email_service.get_emails()


@router.post("/search_emails")
def search_emails(search_query: SearchQuery):
    emails, search_time = search_service.search_emails(search_query.query)

    email_data = [
        {
            "id": email[0],
            "account_id": email[1],
            "subject": email[2],
            "sender": email[3],
            "recipients": email[4],
            "date": email[5],
            "body": email[6],
            "unique_id": email[7],
        }
        for email in emails
    ]

    logging.debug(f"Found {len(email_data)} emails")

    return {"emails": email_data, "search_time": search_time}


@router.get("/email_details/{email_id}")
def email_details(email_id: int):
    logging.debug(f"Received request to get email details for email {email_id}")
    return email_service.get_email_details(email_id)


@router.get("/latest-emails")
def latest_emails():
    logging.debug("Received request to get latest emails")
    return email_service.get_latest_emails()


@router.delete("/delete_email/{email_id}")
def delete_email(email_id: int):
    logging.debug(f"Received request to delete email {email_id}")
    return email_service.delete_email(email_id)

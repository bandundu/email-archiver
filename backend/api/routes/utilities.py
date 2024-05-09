# utilities.py contains the FastAPI router for utility endpoints. It includes endpoints to retrieve the Fernet key and get statistics about the email archive.
import logging

from fastapi import APIRouter
from api.schemas.schemas import SearchQuery
from dateutil import parser
import os
from config.config import config
import services.statistics_service as statistics_service

router = APIRouter()


# Utility Endpoints
def format_date(date_str):
    date_obj = parser.parse(date_str)
    return date_obj.strftime("%a, %d %b %Y %H:%M:%S")


@router.get("/fernet_key")
def get_fernet_key():
    logging.debug("Received request to get Fernet key")
    fernet_key = os.getenv("SECRET_KEY")
    return {"fernet_key": fernet_key}


@router.get("/stats")
def get_stats():
    logging.debug("Received request to get statistics")
    return statistics_service.email_statistics()

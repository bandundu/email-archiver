# Routes are responsible only responsible for handling requests, validating input, and returning responses. They should not contain any business logic. The business logic should be implemented in services.

# attachments.py is responsible for handling requests related to attachments and inline images

from fastapi import APIRouter, Response
from api.schemas.schemas import AccountData

import logging

# Import config
from config.config import config

# Import services
import services.attachment_service as attachment_service

router = APIRouter()


@router.get("/download_attachment/{attachment_id}")
def download_attachment(attachment_id: int):
    logging.debug(f"Received request to download attachment {attachment_id}")
    return attachment_service.download_attachment(attachment_id)


@router.get("/get_inline_image/{cid}")
def get_inline_image(cid: str):
    logging.debug(f"Received request to get inline image {cid}")
    return attachment_service.get_inline_image(cid)

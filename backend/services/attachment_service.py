# Services are used to interact with the database, perform business logic and other necesarry core functions. They are to be imported into the routes. Services should not use FastAPI's Request and Response classes. They should only return data to the routes. The routes will then use this data to return a response to the client.

import logging
import sqlite3
from models.database import get_db
from models.models import Attachment
from config import config
from utils.encryption import cipher_suite
from fastapi import Response


def download_attachment(attachment_id: int):
    logging.debug(f"Received request to download attachment {attachment_id}")

    db = next(get_db())

    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if attachment:
        filename = attachment.filename
        content = attachment.content
        media_type = "application/octet-stream"
        headers = {"Content-Disposition": f"attachment; filename={filename}"}

        return Response(content=content, media_type=media_type, headers=headers)
    else:
        return {"error": "Attachment not found"}


def get_inline_image(cid: str):
    db = next(get_db())

    # check if CID has < and >, if not, add them
    if not cid.startswith("<"):
        cid = "<" + cid
    if not cid.endswith(">"):
        cid = cid + ">"

    attachment = db.query(Attachment).filter(Attachment.cid == cid).first()

    if attachment:
        content = attachment.content
        filename = attachment.filename
        media_type = f"image/{filename.split('.')[-1]}"
        headers = {"Content-Disposition": f"inline; filename={filename}"}
        return {content: content, media_type: media_type, headers: headers}
    else:
        return {"error": "Inline image not found"}

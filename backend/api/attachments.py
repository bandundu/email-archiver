from fastapi import APIRouter, Response
from models import AccountData
import email_archiver as email_archiver
import sqlite3

router = APIRouter()


@router.get("/download_attachment/{attachment_id}")
def download_attachment(attachment_id: int):
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, content FROM attachments WHERE id = ?", (attachment_id,)
    )
    attachment = cursor.fetchone()
    conn.close()

    if attachment:
        filename, content = attachment
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    else:
        return {"error": "Attachment not found"}

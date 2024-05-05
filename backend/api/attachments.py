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

@router.get("/get_inline_image/{cid}")
def get_inline_image(cid: str):
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()
    # check if CID has < and >, if not, add them
    if not cid.startswith("<"):
        cid = "<" + cid
    if not cid.endswith(">"):
        cid = cid + ">"

    cursor.execute(
        "SELECT content, filename FROM attachments WHERE cid = ?",
        (cid,)
    )
    attachment = cursor.fetchone()
    conn.close()

    if attachment:
        content, filename = attachment
        return Response(
            content=content,
            media_type=f"image/{filename.split('.')[-1]}",
            headers={"Content-Disposition": f"inline; filename={filename}"},
        )
    else:
        return {"error": "Inline image not found"}
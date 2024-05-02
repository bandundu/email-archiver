from fastapi import APIRouter, Response
import email_archiver as email_archiver
import sqlite3
from models import SearchQuery

router = APIRouter()


@router.get("/export_email/{email_id}")
def export_email(email_id: int):
    conn = sqlite3.connect("data/email_archive.db")
    email_data = email_archiver.export_email(conn, email_id)
    conn.close()

    if email_data:
        return Response(
            content=email_data,
            media_type="message/rfc822",
            headers={
                "Content-Disposition": f"attachment; filename=email_{email_id}.eml"
            },
        )
    else:
        return {"error": "Email not found"}


@router.get("/export_all_emails")
def export_all_emails():
    conn = sqlite3.connect("data/email_archive.db")
    zip_data = email_archiver.export_all_emails(conn)
    conn.close()

    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=all_emails.zip"},
    )


@router.post("/export_search_results")
def export_search_results(search_query: SearchQuery):
    query = search_query.query
    conn = sqlite3.connect("data/email_archive.db")
    zip_data = email_archiver.export_search_results(conn, query)
    conn.close()

    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=search_results.zip"},
    )

import sqlite3
from fastapi import APIRouter
from api.utilities import format_date
from models import SearchQuery
import email_archiver as email_archiver


router = APIRouter()

# Email Management Endpoints


@router.get("/emails")
def get_emails(
    page: int = 1, per_page: int = 10, sort_by: str = "date", sort_order: str = "desc"
):
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]

    offset = (page - 1) * per_page

    query = f"SELECT * FROM emails ORDER BY {sort_by} {sort_order} LIMIT {per_page} OFFSET {offset}"
    cursor.execute(query)
    emails = cursor.fetchall()

    email_data = []
    for email in emails:
        email_id = email[0]
        cursor.execute(
            "SELECT COUNT(*) FROM attachments WHERE email_id = ?", (email_id,)
        )
        attachment_count = cursor.fetchone()[0]

        email_data.append(
            {
                "id": email_id,
                "account_id": email[1],
                "subject": email[2],
                "sender": email[3],
                "recipients": email[4],
                "date": email[5],
                "body": email[6],
                "unique_id": email[7],
                "has_attachments": attachment_count > 0,
            }
        )

    conn.close()

    return {"emails": email_data, "total_emails": total_emails}


@router.post("/search_emails")
def search_emails(search_query: SearchQuery):
    query = search_query.query
    conn = sqlite3.connect("data/email_archive.db")
    emails = email_archiver.search_emails(conn, query)
    conn.close()

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

    return {"emails": email_data}


@router.get("/email_details/{email_id}")
def email_details(email_id: int):
    conn = sqlite3.connect("data/email_archive.db")
    email, attachments, attachment_filenames = email_archiver.get_email_details(
        conn, email_id
    )
    conn.close()

    if email:
        email_data = {
            "id": email[0],
            "account_id": email[1],
            "subject": email[2],
            "sender": email[3],
            "recipients": email[4],
            "date": email[5],
            "body": email[6],
            "content_type": email[7],
        }

        attachment_data = [
            {"id": attachment[0], "filename": attachment[1]}
            for attachment in attachments
        ]

        # Check if the email body is large
        body_size = len(email[6])
        is_large_file = body_size > 1000000  # Adjust the threshold as needed

        return {
            "email": email_data,
            "attachments": attachment_data,
            "is_large_file": is_large_file,
        }
    else:
        return {"error": "Email not found"}


@router.get("/latest-emails")
def latest_emails():
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT subject, sender, date FROM emails ORDER BY date DESC LIMIT 5"
    )
    latest_emails = cursor.fetchall()

    conn.close()

    emails_data = [
        {"subject": email[0], "sender": email[1], "date": format_date(email[2])}
        for email in latest_emails
    ]

    return emails_data


@router.delete("/delete_email/{email_id}")
def delete_email(email_id: int):
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
        cursor.execute("DELETE FROM attachments WHERE email_id = ?", (email_id,))

        conn.commit()
        conn.close()

        return {"message": "Email deleted successfully"}

    except Exception as e:
        conn.rollback()
        conn.close()
        return {"error": "An error occurred while deleting the email"}

import sqlite3
from fastapi import APIRouter
from models import SearchQuery
import email_archiver as email_archiver
from dateutil import parser
import os


router = APIRouter()


# Utility Endpoints
def format_date(date_str):
    date_obj = parser.parse(date_str)
    return date_obj.strftime("%a, %d %b %Y %H:%M:%S")


@router.get("/fernet_key")
def get_fernet_key():
    fernet_key = os.getenv("SECRET_KEY")
    return {"fernet_key": fernet_key}


@router.get("/stats")
def get_stats():
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM accounts")
    total_accounts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attachments")
    total_attachments = cursor.fetchone()[0]

    conn.close()

    stats = {
        "totalEmails": total_emails,
        "totalAccounts": total_accounts,
        "totalAttachments": total_attachments,
    }
    return stats

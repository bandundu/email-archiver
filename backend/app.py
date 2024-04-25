from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from dateutil import parser
import threading
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet, InvalidToken
import re
import email_archiver as email_archiver
from email_archiver import initialize_database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to load environment variables from .env file
load_dotenv()

# Read the SECRET_KEY from the environment variables
secret_key = os.getenv("SECRET_KEY")

if secret_key:
    # If SECRET_KEY is present and not empty, use it as the Fernet key
    fernet_key = secret_key
    print(f"Using preset Fernet key: {fernet_key}")
else:
    # If SECRET_KEY is empty or not present, generate a new Fernet key
    fernet_key = Fernet.generate_key().decode()
    print(f"Generated new Fernet key: {fernet_key}")

    # Read the contents of the .env file
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_contents = f.read().strip()  # Strip whitespace

        # Check if the file is empty or the first line is empty
        if not env_contents or env_contents.startswith("\n"):
            # Write the new SECRET_KEY on the first line
            updated_contents = f"SECRET_KEY={fernet_key}\n{env_contents.lstrip()}"
        else:
            # Check if SECRET_KEY exists in the .env file
            if "SECRET_KEY=" in env_contents:
                # Update the existing SECRET_KEY with the generated Fernet key
                updated_contents = re.sub(
                    r"SECRET_KEY=.*", f"SECRET_KEY={fernet_key}", env_contents
                )
            else:
                # Append the new SECRET_KEY to the .env file
                updated_contents = env_contents + f"\nSECRET_KEY={fernet_key}"

    else:
        # If the file doesn't exist, create it with the new SECRET_KEY
        updated_contents = f"SECRET_KEY={fernet_key}\n"

    # Write the updated contents back to the .env file
    with open(".env", "w") as f:
        f.write(updated_contents)

class AccountData(BaseModel):
    email: str
    password: str
    protocol: str
    server: str
    port: int

class SearchQuery(BaseModel):
    query: str

def format_date(date_str):
    date_obj = parser.parse(date_str)
    return date_obj.strftime("%a, %d %b %Y %H:%M:%S")

@app.get("/fernet_key")
def get_fernet_key():
    fernet_key = os.getenv("SECRET_KEY")
    return {"fernet_key": fernet_key}

@app.get("/stats")
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

@app.get("/latest-emails")
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

@app.post("/create_account")
def create_account(account_data: AccountData):
    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port

    if not all([email, password, protocol.lower(), server, port]):
        return {"error": "Missing required fields"}

    conn = sqlite3.connect("data/email_archive.db")
    try:
        email_archiver.create_account(conn, email, password, protocol, server, port)
        conn.close()
        return {"message": "Account created successfully"}
    except sqlite3.IntegrityError:
        conn.close()
        error_message = f"An account with email '{email}' already exists. Please use a different email."
        return {"error": error_message}

@app.get("/emails")
def get_emails(page: int = 1, per_page: int = 10, sort_by: str = "date", sort_order: str = "desc"):
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
        cursor.execute("SELECT COUNT(*) FROM attachments WHERE email_id = ?", (email_id,))
        attachment_count = cursor.fetchone()[0]

        email_data.append({
            "id": email_id,
            "account_id": email[1],
            "subject": email[2],
            "sender": email[3],
            "recipients": email[4],
            "date": email[5],
            "body": email[6],
            "unique_id": email[7],
            "has_attachments": attachment_count > 0
        })

    conn.close()

    return {"emails": email_data, "total_emails": total_emails}

@app.get("/get_accounts")
def get_accounts():
    conn = sqlite3.connect("data/email_archive.db")
    accounts = email_archiver.read_accounts(conn)
    conn.close()

    accounts_data = [
        {
            "id": account[0],
            "email": account[1],
            "protocol": account[3],
            "server": account[4],
            "port": account[5],
        }
        for account in accounts
    ]
    return accounts_data

@app.post("/update_account/{account_id}")
def update_account(account_id: int, account_data: AccountData):
    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port
    mailbox = account_data.mailbox

    conn = sqlite3.connect("data/email_archive.db")
    email_archiver.update_account(
        conn, account_id, email, password, protocol.lower(), server, port, mailbox
    )
    conn.close()

    return {"message": "Account updated successfully"}

@app.delete("/delete_account/{account_id}")
def delete_account(account_id: int):
    conn = sqlite3.connect("data/email_archive.db")
    email_archiver.delete_account(conn, account_id)
    conn.close()

    return {"message": "Account deleted successfully"}

@app.delete("/delete_email/{email_id}")
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

@app.post("/search_emails")
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

@app.get("/email_details/{email_id}")
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
        return {"email": email_data, "attachments": attachment_data}
    else:
        return {"error": "Email not found"}

@app.get("/download_attachment/{attachment_id}")
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
        return Response(content=content, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        return {"error": "Attachment not found"}

@app.get("/export_email/{email_id}")
def export_email(email_id: int):
    conn = sqlite3.connect("data/email_archive.db")
    email_data = email_archiver.export_email(conn, email_id)
    conn.close()

    if email_data:
        return Response(content=email_data, media_type="message/rfc822", headers={"Content-Disposition": f"attachment; filename=email_{email_id}.eml"})
    else:
        return {"error": "Email not found"}

@app.get("/export_all_emails")
def export_all_emails():
    conn = sqlite3.connect("data/email_archive.db")
    zip_data = email_archiver.export_all_emails(conn)
    conn.close()

    return Response(content=zip_data, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=all_emails.zip"})

@app.post("/export_search_results")
def export_search_results(search_query: SearchQuery):
    query = search_query.query
    conn = sqlite3.connect("data/email_archive.db")
    zip_data = email_archiver.export_search_results(conn, query)
    conn.close()

    return Response(content=zip_data, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=search_results.zip"})

def run_archiver_thread():
    email_archiver.run_archiver()

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        initialize_database()
    except InvalidToken:
        print(
            "Error: The provided Fernet key is incompatible with the existing database."
        )
        exit(1)

    archiver_thread = threading.Thread(target=run_archiver_thread)
    archiver_thread.daemon = True
    archiver_thread.start()

    import uvicorn
    uvicorn.run(app, host="localhost", port=5050)
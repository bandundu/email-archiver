from flask import Flask, request, make_response, jsonify

import sqlite3
from dateutil import parser
import threading
from dotenv import load_dotenv
# from flask_cors import CORS
import os
from cryptography.fernet import Fernet, InvalidToken
import re

app = Flask(__name__)
# cors = CORS(
#     app,
#     origins="*",
#     supports_credentials=True,
# )


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

import email_archiver as email_archiver
from email_archiver import initialize_database


@app.template_filter("format_date")
def format_date(date_str):
    # Use dateutil.parser to handle various date formats with or without timezone information
    date_obj = parser.parse(date_str)
    # Format the date as desired (e.g., without timezone information)
    return date_obj.strftime("%a, %d %b %Y %H:%M:%S")


@app.route("/fernet_key")
def get_fernet_key():
    fernet_key = os.getenv("SECRET_KEY")
    return jsonify({"fernet_key": fernet_key})


@app.route("/stats")
def get_stats():
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    # Fetch summary statistics
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
    response = make_response(jsonify(stats))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
    # return jsonify(stats)


@app.route("/latest-emails")
def latest_emails():
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    # Fetch the latest archived emails
    cursor.execute(
        "SELECT subject, sender, date FROM emails ORDER BY date DESC LIMIT 5"
    )
    latest_emails = cursor.fetchall()

    conn.close()

    # Format the latest emails as a list of dictionaries
    emails_data = [
        {"subject": email[0], "sender": email[1], "date": format_date(email[2])}
        for email in latest_emails
    ]

    return jsonify(emails_data)


@app.route("/create_account", methods=["POST", "OPTIONS"])
def create_account():
    if request.method == "OPTIONS":
        # Preflight request. Reply with the CORS headers.
        response = make_response()
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    if request.method == "POST":
        # Parse data as JSON
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        protocol = data.get("protocol")
        server = data.get("server")
        port = data.get("port")

        # Validate the extracted data
        if not all([email, password, protocol.lower(), server, port]):
            response = jsonify({"error": "Missing required fields"})
            response.headers.add("Access-Control-Allow-Headers", "*")
            response.headers.add("Access-Control-Allow-Methods", "*")
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 400

        conn = sqlite3.connect("data/email_archive.db")
        try:
            # Assume email_archiver.create_account function exists and handles the DB operations
            email_archiver.create_account(conn, email, password, protocol, server, port)
            conn.close()
            response = jsonify({"message": "Account created successfully"})
            response.headers.add("Access-Control-Allow-Headers", "*")
            response.headers.add("Access-Control-Allow-Methods", "*")
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 201
        except sqlite3.IntegrityError:
            conn.close()
            error_message = f"An account with email '{email}' already exists. Please use a different email."
            response = jsonify({"error": error_message})
            response.headers.add("Access-Control-Allow-Headers", "*")
            response.headers.add("Access-Control-Allow-Methods", "*")
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 400


@app.route("/emails")
def get_emails():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    sort_by = request.args.get("sort_by", default="date")
    sort_order = request.args.get("sort_order", default="desc")

    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    # Get the total count of emails
    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]

    # Calculate the offset based on the page and per_page values
    offset = (page - 1) * per_page

    # Fetch the emails with pagination
    query = f"SELECT * FROM emails ORDER BY {sort_by} {sort_order} LIMIT {per_page} OFFSET {offset}"
    cursor.execute(query)
    emails = cursor.fetchall()

    email_data = []
    for email in emails:
        email_id = email[0]
        # Check if the email has attachments
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

    response = make_response(
        jsonify({"emails": email_data, "total_emails": total_emails})
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route("/get_accounts", methods=["GET"])
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
    # create response and set CORS headers
    response = jsonify(accounts_data)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route("/update_account/<int:account_id>", methods=["POST"])
def update_account(account_id):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    protocol = data.get("protocol")
    server = data.get("server")
    port = int(data.get("port"))
    mailbox = data.get("mailbox")

    conn = sqlite3.connect("data/email_archive.db")
    email_archiver.update_account(
        conn, account_id, email, password, protocol.lower(), server, port, mailbox
    )
    conn.close()

    return jsonify({"message": "Account updated successfully"}), 200


@app.route("/delete_account/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    conn = sqlite3.connect("data/email_archive.db")
    email_archiver.delete_account(conn, account_id)
    conn.close()

    return jsonify({"message": "Account deleted successfully"}), 200


@app.route("/delete_email/<int:email_id>", methods=["DELETE"])
def delete_email(email_id):
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    try:
        # Delete the email from the emails table
        cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))

        # Delete the associated attachments from the attachments table
        cursor.execute("DELETE FROM attachments WHERE email_id = ?", (email_id,))

        conn.commit()
        conn.close()

        # create response and set CORS headers
        response = jsonify({"message": "Email deleted successfully"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        conn.rollback()
        conn.close()
        # create response and set CORS headers
        response = jsonify({"error": "An error occurred while deleting the email"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


@app.route("/search_emails", methods=["POST"])
def search_emails():
    query = request.get_json().get("query")
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

    response = jsonify({"emails": email_data})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/email_details/<int:email_id>")
def email_details(email_id):
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
        # create response and set CORS headers
        response = jsonify({"email": email_data, "attachments": attachment_data})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        # create response and set CORS headers
        response = jsonify({"error": "Email not found"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


@app.route("/download_attachment/<int:attachment_id>")
def download_attachment(attachment_id):
    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, content FROM attachments WHERE id = ?", (attachment_id,)
    )
    attachment = cursor.fetchone()
    conn.close()

    if attachment:
        filename, content = attachment
        response = make_response(content)
        response.headers.set("Content-Type", "application/octet-stream")
        response.headers.set("Content-Disposition", "attachment", filename=filename)
        # add CORS headers
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        # create response and set CORS headers
        response = jsonify({"error": "Attachment not found"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route("/export_email/<int:email_id>")
def export_email(email_id):
    conn = sqlite3.connect("data/email_archive.db")
    email_data = email_archiver.export_email(conn, email_id)
    conn.close()

    if email_data:
        response = make_response(email_data)
        response.headers.set("Content-Type", "message/rfc822")
        response.headers.set(
            "Content-Disposition", "attachment", filename=f"email_{email_id}.eml"
        )
        # add CORS headers
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        # create response and set CORS headers
        response = jsonify({"error": "Email not found"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


@app.route("/export_all_emails")
def export_all_emails():
    conn = sqlite3.connect("data/email_archive.db")
    zip_data = email_archiver.export_all_emails(conn)
    conn.close()

    response = make_response(zip_data)
    response.headers.set("Content-Type", "application/zip")
    response.headers.set("Content-Disposition", "attachment", filename="all_emails.zip")
    # add CORS headers
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/export_search_results", methods=["POST"])
def export_search_results():
    query = request.get_json().get("query")
    conn = sqlite3.connect("data/email_archive.db")
    zip_data = email_archiver.export_search_results(conn, query)
    conn.close()

    response = make_response(zip_data)
    response.headers.set("Content-Type", "application/zip")
    response.headers.set(
        "Content-Disposition", "attachment", filename="search_results.zip"
    )
    # add CORS headers
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def run_archiver_thread():
    email_archiver.run_archiver()


if __name__ == "__main__":
    # Check if the "data" folder exists, and create it if it doesn't
    if not os.path.exists("data"):
        os.makedirs("data")

    # Initialize the database
    try:
        initialize_database()
    except InvalidToken:
        print(
            "Error: The provided Fernet key is incompatible with the existing database."
        )
        exit(1)
    # Start the email archiving thread
    archiver_thread = threading.Thread(target=run_archiver_thread)
    archiver_thread.daemon = True
    archiver_thread.start()

    # Run the Flask app
    app.run(host="0.0.0.0", port=5050, debug=True)

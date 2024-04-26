import argparse
import imaplib
import io
import poplib
import email
import sqlite3
import time
import logging
import re
import traceback
import zipfile
from cryptography.fernet import Fernet
import os
from datetime import datetime
from email.utils import parsedate_to_datetime
from dateutil import parser
from dotenv import load_dotenv
from jwt import InvalidTokenError
import hashlib


# Load environment variables from .env file
load_dotenv()

# Load the secret key from the environment variable
secret_key = os.environ.get("SECRET_KEY").encode()
# In email_archiver.py
cipher_suite = Fernet(secret_key)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def initialize_database():
    db_exists = os.path.exists("data/email_archive.db")
    if not db_exists:
        # Connect to the database. This will create the file if it does not exist.
        conn = sqlite3.connect("data/email_archive.db")
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS accounts
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           email TEXT UNIQUE,
                           password TEXT,
                           protocol TEXT,
                           server TEXT,
                           port INTEGER,
                           mailbox TEXT,
                           interval INTEGER DEFAULT 300)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS emails
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_id INTEGER,
                        subject TEXT,
                        sender TEXT,
                        recipients TEXT,
                        date DATETIME,
                        body TEXT,
                        fingerprint TEXT UNIQUE,
                        FOREIGN KEY (account_id) REFERENCES accounts (id))"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS attachments
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           email_id INTEGER,
                           filename TEXT,
                           content BLOB,
                           FOREIGN KEY (email_id) REFERENCES emails (id))"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS email_uids
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           account_id INTEGER,
                           uid TEXT,
                           FOREIGN KEY (account_id) REFERENCES accounts (id))"""
        )

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    else:
        logging.info("Database already exists.")


DEFAULT_PROTOCOL = "pop3"  # Use POP3 as the default protocol


def parse_date(date_str):
    if date_str is None:
        return None
    try:
        date_tuple = parsedate_to_datetime(date_str)
        return date_tuple.strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None


import hashlib

def fetch_and_archive_emails(
    conn, account_id, protocol, server, port, username, encrypted_password, mailbox=None
):
    try:
        logging.info(f"Started email archiving for account {account_id}.")
        if not isinstance(encrypted_password, bytes):
            encrypted_password = encrypted_password.encode()
        try:
            password = cipher_suite.decrypt(encrypted_password).decode()
        except InvalidTokenError as e:
            logging.error(f"Decryption Error for account {account_id}: {str(e)}")
            return

        if protocol == "imap":
            client = imaplib.IMAP4_SSL(server, port)
            client._mode_utf8()
            client.login(username, password)
            client.select(mailbox, readonly=True)
            _, data = client.uid("search", None, "ALL")
            email_uids = data[0].split()
        elif protocol == "pop3":
            client = poplib.POP3_SSL(server, port)
            client.user(username)
            client.pass_(password)
            num_emails = len(client.list()[1])
            email_uids = range(1, num_emails + 1)

        total_emails = len(email_uids)
        logging.info(f"Found {total_emails} emails for account {account_id}.")

        cursor = conn.cursor()

        emails_to_insert = []
        attachments_to_insert = []
        skipped_emails = 0
        failed_emails = 0

        for uid in email_uids:
            if protocol == "imap":
                _, data = client.uid("fetch", uid, "(RFC822)")
                if not data or not data[0] or data[0] is None:
                    logging.warning(f"Failed to fetch email with UID {uid} for account {account_id}.")
                    failed_emails += 1
                    continue
                raw_email = data[0][1]
            elif protocol == "pop3":
                raw_email = b"\n".join(client.retr(uid)[1])

            email_message = email.message_from_bytes(raw_email)

            subject = decode_header(email_message["Subject"])
            sender = decode_header(email_message["From"])
            recipients = decode_header(email_message["To"])
            date = email_message["Date"]
            message_id = email_message["Message-ID"]

            # Generate email fingerprint
            fingerprint_data = f"{subject}|{sender}|{recipients}|{date}|{message_id}"
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

            # Check if the email already exists in the database using the fingerprint
            cursor.execute("SELECT id FROM emails WHERE fingerprint = ?", (fingerprint,))
            existing_email = cursor.fetchone()
            if existing_email:
                logging.debug(f"Skipping email with UID {uid} for account {account_id} as it already exists.")
                skipped_emails += 1
                continue

            body = extract_body(email_message)
            parsed_date = parse_date(date)

            emails_to_insert.append((account_id, subject, sender, recipients, parsed_date, body, fingerprint))

            for part in email_message.walk():
                if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                    continue

                filename = decode_filename(part.get_filename())
                if filename:
                    content = part.get_payload(decode=True)
                    attachments_to_insert.append((len(emails_to_insert), filename, content))

        new_emails = len(emails_to_insert)
        new_attachments = len(attachments_to_insert)

        if emails_to_insert:
            cursor.executemany(
                """INSERT INTO emails (account_id, subject, sender, recipients, date, body, fingerprint)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)""",
                emails_to_insert,
            )
            logging.info(f"Inserted {new_emails} new emails for account {account_id} into the database.")

        if attachments_to_insert:
            cursor.executemany(
                """INSERT INTO attachments (email_id, filename, content)
                                  VALUES (?, ?, ?)""",
                attachments_to_insert,
            )
            logging.info(f"Saved {new_attachments} new attachments for account {account_id}.")

        conn.commit()

        if protocol == "imap":
            client.close()
            client.logout()
        elif protocol == "pop3":
            client.quit()

        logging.info(f"Email archiving completed successfully for account {account_id}.")
        logging.info(f"Total emails found: {total_emails}")
        logging.info(f"New emails inserted: {new_emails}")
        logging.info(f"Skipped emails (already exists): {skipped_emails}")
        logging.info(f"Failed emails (fetching error): {failed_emails}")
        logging.info(f"New attachments saved: {new_attachments}")

    except Exception as e:
        logging.error(f"An error occurred during email archiving for account {account_id}: {str(e)}")
        logging.error(f"Exception details: {traceback.format_exc()}")


def decode_header(header):
    if header is None:
        return ""
    parts = email.header.decode_header(header)
    decoded_parts = [part.decode(encoding or "utf-8") if isinstance(part, bytes) else part for part, encoding in parts]
    return "".join(decoded_parts)


def extract_body(email_message):
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                body += payload.decode(charset or "utf-8", errors="replace")
    else:
        payload = email_message.get_payload(decode=True)
        charset = email_message.get_content_charset()
        body = payload.decode(charset or "utf-8", errors="replace")
    return body


def decode_filename(filename):
    if filename is None:
        return ""
    parts = email.header.decode_header(filename)
    decoded_parts = [part.decode(encoding or "utf-8") if isinstance(part, bytes) else part for part, encoding in parts]
    return "".join(decoded_parts)


def decode_header(header):
    if header is None:
        return ""
    parts = email.header.decode_header(header)
    decoded_parts = [part.decode(encoding or "utf-8") if isinstance(part, bytes) else part for part, encoding in parts]
    return "".join(decoded_parts)


def extract_body(email_message):
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                body += payload.decode(charset or "utf-8", errors="replace")
    else:
        payload = email_message.get_payload(decode=True)
        charset = email_message.get_content_charset()
        body = payload.decode(charset or "utf-8", errors="replace")
    return body


def decode_filename(filename):
    if filename is None:
        return ""
    parts = email.header.decode_header(filename)
    decoded_parts = [part.decode(encoding or "utf-8") if isinstance(part, bytes) else part for part, encoding in parts]
    return "".join(decoded_parts)


def create_account(conn, email, password, protocol, server, port, interval=300):
    logging.info(f"Creating {protocol.upper()} account for {email}.")
    mailbox = "INBOX" if protocol == "imap" else None

    try:
        if protocol == "imap":
            client = imaplib.IMAP4_SSL(server, int(port))
            client._mode_utf8()
            client.login(email, password)
            client.logout()
        elif protocol == "pop3":
            client = poplib.POP3_SSL(server, int(port))
            client.user(email)
            client.pass_(password)
            client.quit()

        # Encrypt the password
        encrypted_password = cipher_suite.encrypt(password.encode())

        cursor = conn.cursor()
        cursor.execute(
        """INSERT INTO accounts (email, password, protocol, server, port, mailbox, interval)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (email, encrypted_password, protocol, server, int(port), mailbox, interval),
        )
        account_id = cursor.lastrowid
        conn.commit()
        logging.info(f"{protocol.upper()} account created successfully for {email}.")

        # Run email archiving for the newly created account TODO: adjust this as it creates duplicate records on application start
        # run_archiver_once(account_id)

        return account_id
    except (imaplib.IMAP4.error, poplib.error_proto) as e:
        logging.error(
            f"Failed to create {protocol.upper()} account for {email}. Error: {str(e)}"
        )
        print(
            f"Failed to create {protocol.upper()} account. Please check the {protocol.upper()} server and port manually."
        )
        return None
    except sqlite3.IntegrityError:
        logging.warning(
            f"{protocol.upper()} account with email {email} already exists in the database."
        )
        print(
            f"An account with email {email} already exists. Please use a different email."
        )
        return None


def read_accounts(conn):
    logging.info("Fetching all IMAP/POP3 accounts from the database.")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    logging.info(f"Retrieved {len(accounts)} IMAP/POP3 accounts from the database.")
    return accounts


def get_account(conn, account_id):
    logging.info(f"Fetching account details for account ID {account_id}.")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    account = cursor.fetchone()
    if account:
        logging.info(
            f"Account details fetched successfully for account ID {account_id}."
        )
        return account
    else:
        logging.warning(f"Account with ID {account_id} not found.")
        return None


def update_account(conn, account_id, email, password, protocol, server, port, mailbox, interval):
    logging.info(f"Updating account {account_id} with email {email}.")

    # Encrypt the new password
    encrypted_password = cipher_suite.encrypt(password.encode())

    cursor = conn.cursor()
    cursor.execute(
        """UPDATE accounts
                      SET email = ?, password = ?, protocol = ?, server = ?, port = ?, mailbox = ?, interval = ?
                      WHERE id = ?""",
        (email, encrypted_password, protocol, server, port, mailbox, interval, account_id),
    )
    conn.commit()
    logging.info(f"Account {account_id} updated successfully.")


def delete_account(conn, account_id):
    logging.info(f"Deleting account {account_id}.")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    logging.info(f"Account {account_id} deleted successfully.")


def export_email(conn, email_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
    email = cursor.fetchone()

    if email:
        email_data = email[-1]  # Assuming the last column contains the raw email data
        return email_data
    else:
        return None


def export_all_emails(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for email in emails:
            email_id = email[0]
            email_data = email[
                -1
            ]  # Assuming the last column contains the raw email data
            zip_file.writestr(f"email_{email_id}.eml", email_data)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def export_search_results(conn, query):
    emails = search_emails(conn, query)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for email in emails:
            email_id = email[0]
            email_data = email[
                -1
            ]  # Assuming the last column contains the raw email data
            zip_file.writestr(f"email_{email_id}.eml", email_data)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def search_emails(conn, query):
    logging.info(f"Searching for emails with query: {query}")
    cursor = conn.cursor()

    # Remove leading/trailing whitespaces and convert to lowercase
    query = query.strip().lower()

    # Check if the query is empty
    if not query:
        logging.info("Empty search query. Returning no results.")
        return []  # Return an empty list

    # Check if the query contains a date range
    date_range_pattern = r"(\d{1,2}\s+\w{3}\s+\d{4})\s*-\s*(\d{1,2}\s+\w{3}\s+\d{4})"
    date_range_match = re.search(date_range_pattern, query)

    if date_range_match:
        start_date_str, end_date_str = date_range_match.groups()
        try:
            start_date = parser.parse(start_date_str, fuzzy=True).strftime("%Y-%m-%d")
            end_date = parser.parse(end_date_str, fuzzy=True).strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT * FROM emails WHERE date BETWEEN ? AND ?",
                (start_date, end_date),
            )
            emails = cursor.fetchall()
            logging.info(f"Found {len(emails)} emails within the date range.")
            return emails
        except (ValueError, TypeError):
            logging.info("Invalid date range format. Proceeding with normal search.")
    else:
        # Check if the query is a valid date string
        try:
            query_date = parser.parse(query, fuzzy=True)
            date_query = query_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            date_query = None

        if date_query:
            # Search emails by date (case-insensitive)
            cursor.execute(
                "SELECT * FROM emails WHERE LOWER(date) LIKE ?", (f"%{date_query}%",)
            )
        else:
            # Split the query into individual terms
            query_terms = re.findall(r"\b\w+\b", query)

            # Check if there are any valid search terms
            if not query_terms:
                logging.info("No valid search terms found. Returning no results.")
                return []  # Return an empty list

            # Build the SQL query dynamically based on the number of query terms
            sql_query = "SELECT * FROM emails WHERE "
            sql_conditions = []
            sql_params = []

            for term in query_terms:
                sql_conditions.append(
                    "(LOWER(subject) LIKE ? OR LOWER(sender) LIKE ? OR LOWER(recipients) LIKE ? OR LOWER(body) LIKE ?)"
                )
                sql_params.extend([f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%"])

            sql_query += " OR ".join(sql_conditions)

            # Execute the SQL query with the dynamic conditions and parameters
            cursor.execute(sql_query, sql_params)

    emails = cursor.fetchall()
    logging.info(f"Found {len(emails)} emails matching the search query.")
    return emails


def get_email_details(conn, email_id):
    logging.info(f"Fetching email details for email ID {email_id}.")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT *, (SELECT GROUP_CONCAT(filename) FROM attachments WHERE email_id = emails.id) AS attachment_filenames FROM emails WHERE id = ?",
        (email_id,),
    )
    email = cursor.fetchone()

    cursor.execute(
        "SELECT id, filename FROM attachments WHERE email_id = ?", (email_id,)
    )
    attachments = cursor.fetchall()

    html_tags = re.compile(r"<(?!!)(?P<tag>[a-zA-Z]+).*?>", re.IGNORECASE)
    code_block_pattern = re.compile(r"```.*?```", re.DOTALL)

    if email:
        content_type = "text/plain"
        logging.info(f"Email with ID {email_id} is a plain text email.")

        if (
            "<!doctype html>" in email[6].lower()
            or "<html" in email[6].lower()
            or html_tags.search(email[6]) is not None
        ):
            content_type = "text/html"
            logging.info(f"Email with ID {email_id} is an HTML email.")

            # Replace code blocks with <pre><code> tags
            body = code_block_pattern.sub(
                lambda match: f"<pre><code>{match.group()[3:-3]}</code></pre>", email[6]
            )

            # Extract the HTML portion of the email
            html_start = (
                body.lower().find("<!doctype html>")
                if "<!doctype html>" in body.lower()
                else body.lower().find("<html")
            )
            html_end = body.lower().rfind("</html>") + len("</html>")
            if html_start != -1 and html_end != -1:
                email = (
                    email[:6] + (body[html_start:html_end], content_type) + (email[-1],)
                )
            else:
                email = email[:6] + (body, content_type) + (email[-1],)
        else:
            # Replace code blocks with <pre><code> tags
            body = code_block_pattern.sub(
                lambda match: f"<pre><code>{match.group()[3:-3]}</code></pre>", email[6]
            )
            email = email[:6] + (body, content_type) + (email[-1],)

        attachment_filenames = email[-1].split(",") if email[-1] else []
        logging.info(
            f"Email details and attachments fetched successfully for email ID {email_id}."
        )
        return email, attachments, attachment_filenames

    else:
        logging.warning(f"Email with ID {email_id} not found.")
        return None, None, None


def run_archiver_once(account_id):
    try:
        logging.info(f"Starting email archiving for account {account_id}...")
        conn = sqlite3.connect("data/email_archive.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        if account:
            account_id, email, encrypted_password, protocol, server, port, mailbox, interval = account
            fetch_and_archive_emails(
                conn,
                account_id,
                protocol,
                server,
                port,
                email,
                encrypted_password,
                mailbox,
            )
        else:
            logging.warning(f"Account with ID {account_id} not found.")
        conn.close()
        logging.info(f"Email archiving completed for account {account_id}.")
    except Exception as e:
        logging.error(
            f"An error occurred during email archiving for account {account_id}: {str(e)}"
        )
        logging.error(f"Exception details: {traceback.format_exc()}")


def run_archiver():
    while True:
        try:
            logging.info("Starting email archiving cycle...")
            conn = sqlite3.connect("data/email_archive.db")
            accounts = read_accounts(conn)
            
            if not accounts:
                logging.info("No accounts found. Waiting for 5 minutes before the next archiving cycle.")
                conn.close()
                time.sleep(30)  # Wait for 5 minutes before the next cycle if no accounts are available
                continue
            
            for account in accounts:
                account_id, email, encrypted_password, protocol, server, port, mailbox, interval = account
                fetch_and_archive_emails(
                    conn,
                    account_id,
                    protocol,
                    server,
                    port,
                    email,
                    encrypted_password,
                    mailbox,
                )
                logging.info(f"Email archiving completed for account {account_id}. Waiting for {interval} seconds before the next archiving cycle.")
                time.sleep(interval)  # Wait for the specified interval before processing the next account
            
            conn.close()
            logging.info("Email archiving cycle completed.")
        except Exception as e:
            logging.error(f"An error occurred during email archiving: {str(e)}")
            logging.error(f"Exception details: {traceback.format_exc()}")
            time.sleep(300)  # Wait for 5 minutes before retrying in case of an error


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email Archiver CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # IMAP/POP3 Account Management
    parser_create_account = subparsers.add_parser(
        "create_account", help="Create a new IMAP/POP3 account"
    )
    parser_create_account.add_argument("email", help="Email address")
    parser_create_account.add_argument("password", help="Email password")
    parser_create_account.add_argument(
        "--protocol",
        choices=["imap", "pop3"],
        help="Email protocol (imap or pop3)",
        default=DEFAULT_PROTOCOL,
    )

    parser_list_accounts = subparsers.add_parser(
        "list_accounts", help="List all IMAP/POP3 accounts"
    )

    parser_update_account = subparsers.add_parser(
        "update_account", help="Update an IMAP/POP3 account"
    )
    parser_update_account.add_argument("account_id", type=int, help="Account ID")
    parser_update_account.add_argument("email", help="Email address")
    parser_update_account.add_argument("password", help="Email password")
    parser_update_account.add_argument(
        "protocol", choices=["imap", "pop3"], help="Email protocol (imap or pop3)"
    )
    parser_update_account.add_argument("server", help="Email server")
    parser_update_account.add_argument("port", type=int, help="Email server port")
    parser_update_account.add_argument("mailbox", help="Mailbox to archive (IMAP only)")

    parser_delete_account = subparsers.add_parser(
        "delete_account", help="Delete an IMAP/POP3 account"
    )
    parser_delete_account.add_argument("account_id", type=int, help="Account ID")

    # Email Archive
    parser_search_emails = subparsers.add_parser(
        "search_emails", help="Search for emails"
    )
    parser_search_emails.add_argument("query", help="Search query")

    parser_get_email = subparsers.add_parser("get_email", help="Get email details")
    parser_get_email.add_argument("email_id", type=int, help="Email ID")

    # Archiver
    parser_run_archiver = subparsers.add_parser(
        "run_archiver", help="Run the email archiver"
    )

    args = parser.parse_args()

    logging.info(f"Executing command: {args.command}")

    if args.command == "create_account":
        create_account(args.email, args.password, args.protocol)
    elif args.command == "list_accounts":
        accounts = read_accounts()
        for account in accounts:
            print(account)
    elif args.command == "update_account":
        update_account(
            args.account_id,
            args.email,
            args.password,
            args.protocol,
            args.server,
            args.port,
            args.mailbox,
        )
    elif args.command == "delete_account":
        delete_account(args.account_id)
    elif args.command == "search_emails":
        emails = search_emails(args.query)
        for email in emails:
            print(email)
    elif args.command == "get_email":
        email, attachments = get_email_details(args.email_id)
        if email:
            print(email)
            print("Attachments:")
            for attachment in attachments:
                print(attachment)
        else:
            print(f"Email with ID {args.email_id} not found.")
    elif args.command == "run_archiver":
        run_archiver()

    logging.info(f"Command {args.command} executed successfully.")

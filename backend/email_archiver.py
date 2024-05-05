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
import time
from encryption import cipher_suite


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_database_connection():
    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        initialize_database()
        conn = sqlite3.connect("data/email_archive.db")
        return conn
    except InvalidToken:
        print("Error: The provided Fernet key is incompatible with the existing database.")
        exit(1)

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
                           available_inboxes TEXT,
                           selected_inboxes TEXT,
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
        #logging.info("Database already exists.")
        pass


DEFAULT_PROTOCOL = "pop3"  # Use POP3 as the default protocol


def parse_date(date_str):
    if date_str is None:
        return None
    try:
        date_tuple = parsedate_to_datetime(date_str)
        return date_tuple.strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None


def fetch_and_archive_emails(
    conn, account_id, protocol, server, port, username, encrypted_password, selected_inboxes=None
):
    start_time = time.time()
    try:
        logging.info(f"Started email archiving for account {account_id}.")
        if not isinstance(encrypted_password, bytes):
            encrypted_password = encrypted_password.encode()
        try:
            password = cipher_suite.decrypt(encrypted_password).decode()
        except InvalidTokenError as e:
            logging.error(f"Decryption Error for account {account_id}: {str(e)}")
            return 0

        cursor = conn.cursor()
        cursor.execute("SELECT uid FROM email_uids WHERE account_id = ?", (account_id,))
        last_uid = cursor.fetchone()

        if protocol == "imap":
            client = imaplib.IMAP4_SSL(server, port)
            client._mode_utf8()
            client.login(username, password)
            
            if selected_inboxes:
                inboxes = selected_inboxes.split(",")
            else:
                _, mailboxes = client.list()
                inboxes = [mailbox.decode().split('"')[-1] for mailbox in mailboxes]

            for inbox in inboxes:
                if inbox:  # Check if inbox is not empty
                    
                    client.select(inbox, readonly=True)
                    _, data = client.uid("search", None, "ALL")
                    all_uids = data[0].split()

                    if last_uid:
                        _, data = client.uid("search", None, f"UID {last_uid[0]}:*")
                        email_uids = data[0].split()
                    else:
                        email_uids = all_uids

                    if all_uids:
                        _, data = client.status(inbox, "(UIDNEXT)")
                        uidnext = data[0].decode().split()[-1].strip(")")
                    else:
                        uidnext = None

                    if email_uids:
                        email_uids_str = [uid.decode() for uid in email_uids]
                        _, data = client.uid("fetch", ",".join(email_uids_str), "(BODY.PEEK[])")
                        raw_emails = []
                        for item in data:
                            if isinstance(item, tuple) and len(item) > 1:
                                raw_emails.append(item[1])
                    else:
                        raw_emails = []

                    total_emails = len(email_uids)
                    logging.info(f"Found {total_emails} new emails for account {account_id} in inbox {inbox}.")

                    skipped_emails = 0
                    failed_emails = 0
                    total_attachments_inserted = 0
                    new_emails_inserted = 0

                    for uid, raw_email in zip(email_uids, raw_emails):
                        if not raw_email:
                            logging.warning(f"Failed to fetch email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} in inbox {inbox}.")
                            failed_emails += 1
                            continue

                        email_message = email.message_from_bytes(raw_email)

                        subject = decode_header(email_message["Subject"])
                        sender = decode_header(email_message["From"])
                        recipients = decode_header(email_message["To"])
                        date = email_message["Date"]
                        message_id = email_message["Message-ID"]

                        fingerprint_data = f"{subject}|{sender}|{recipients}|{date}|{message_id}"
                        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

                        cursor.execute("SELECT id FROM emails WHERE fingerprint = ?", (fingerprint,))
                        existing_email = cursor.fetchone()
                        if existing_email:
                            logging.debug(f"Skipping email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} in inbox {inbox} as it already exists.")
                            skipped_emails += 1
                            continue

                        body = extract_body(email_message)
                        parsed_date = parse_date(date)

                        cursor.execute(
                            """INSERT INTO emails (account_id, subject, sender, recipients, date, body, fingerprint)
                                          VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (account_id, subject, sender, recipients, parsed_date, body, fingerprint),
                        )
                        email_id = cursor.lastrowid
                        new_emails_inserted += 1

                        attachments_inserted = 0
                        for part in email_message.walk():
                            if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                                continue

                            filename = decode_filename(part.get_filename())
                            if filename:
                                content = part.get_payload(decode=True)
                                cursor.execute(
                                    """INSERT INTO attachments (email_id, filename, content)
                                                  VALUES (?, ?, ?)""",
                                    (email_id, filename, content),
                                )
                                attachments_inserted += 1

                        conn.commit()
                        logging.info(f"Inserted email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} in inbox {inbox} into the database.")

                        if attachments_inserted > 0:
                            logging.info(f"Saved {attachments_inserted} attachment(s) for email with UID {uid.decode() if isinstance(uid, bytes) else uid} and account {account_id} in inbox {inbox}.")
                            total_attachments_inserted += attachments_inserted

                    if uidnext:
                        cursor.execute("INSERT OR REPLACE INTO email_uids (account_id, uid) VALUES (?, ?)", (account_id, uidnext))

            client.close()
            client.logout()

        elif protocol == "pop3":
            client = poplib.POP3_SSL(server, port)
            client.user(username)
            client.pass_(password)
            if last_uid:
                num_emails = len(client.list()[1])
                email_uids = range(last_uid[0] + 1, num_emails + 1)
            else:
                num_emails = len(client.list()[1])
                email_uids = range(1, num_emails + 1)

            raw_emails = [b"\n".join(client.retr(uid)[1]) for uid in email_uids]
            client.quit()

            total_emails = len(email_uids)
            logging.info(f"Found {total_emails} new emails for account {account_id}.")

            skipped_emails = 0
            failed_emails = 0
            total_attachments_inserted = 0
            new_emails_inserted = 0

            for uid, raw_email in zip(email_uids, raw_emails):
                if not raw_email:
                    logging.warning(f"Failed to fetch email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id}.")
                    failed_emails += 1
                    continue

                email_message = email.message_from_bytes(raw_email)

                subject = decode_header(email_message["Subject"])
                sender = decode_header(email_message["From"])
                recipients = decode_header(email_message["To"])
                date = email_message["Date"]
                message_id = email_message["Message-ID"]

                fingerprint_data = f"{subject}|{sender}|{recipients}|{date}|{message_id}"
                fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

                cursor.execute("SELECT id FROM emails WHERE fingerprint = ?", (fingerprint,))
                existing_email = cursor.fetchone()
                if existing_email:
                    logging.debug(f"Skipping email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} as it already exists.")
                    skipped_emails += 1
                    continue

                body = extract_body(email_message)
                parsed_date = parse_date(date)

                cursor.execute(
                    """INSERT INTO emails (account_id, subject, sender, recipients, date, body, fingerprint)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (account_id, subject, sender, recipients, parsed_date, body, fingerprint),
                )
                email_id = cursor.lastrowid
                new_emails_inserted += 1

                attachments_inserted = 0
                for part in email_message.walk():
                    if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                        continue

                    filename = decode_filename(part.get_filename())
                    if filename:
                        content = part.get_payload(decode=True)
                        cursor.execute(
                            """INSERT INTO attachments (email_id, filename, content)
                                          VALUES (?, ?, ?)""",
                            (email_id, filename, content),
                        )
                        attachments_inserted += 1

                conn.commit()
                logging.info(f"Inserted email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} into the database.")

                if attachments_inserted > 0:
                    logging.info(f"Saved {attachments_inserted} attachment(s) for email with UID {uid.decode() if isinstance(uid, bytes) else uid} and account {account_id}.")
                    total_attachments_inserted += attachments_inserted

        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        elapsed_time_str = f"{minutes:02d}:{seconds:02d}"

        logging.info(f"Email archiving completed successfully for account {account_id}.")
        logging.info(f"Execution time: {elapsed_time_str}")
        logging.info(f"Total emails found: {total_emails}")
        logging.info(f"Skipped emails (already exists): {skipped_emails}")
        logging.info(f"Failed emails (fetching error): {failed_emails}")
        logging.info(f"New emails inserted: {new_emails_inserted}")
        logging.info(f"New attachments saved: {total_attachments_inserted}")
        logging.info("-" * 50)

        return new_emails_inserted

    except Exception as e:
        logging.error(f"An error occurred during email archiving for account {account_id}: {str(e)}")
        logging.error(f"Exception details: {traceback.format_exc()}")
        return 0


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


def create_account(conn, email, password, protocol, server, port, interval=300, selected_inboxes=None):
    logging.info(f"Creating {protocol.upper()} account for {email}.")
    mailbox = "INBOX" if protocol == "imap" else None

    # Ensure that the selected_inboxes list has no leading/trailing whitespaces
    if selected_inboxes:
        selected_inboxes = [inbox.strip() for inbox in selected_inboxes]


    try:
        encrypted_password = cipher_suite.encrypt(password.encode())

        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO accounts (email, password, protocol, server, port, mailbox, selected_inboxes, interval)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (email, encrypted_password, protocol, server, int(port), mailbox, ",".join(selected_inboxes) if selected_inboxes else None, interval),
        )
        account_id = cursor.lastrowid
        conn.commit()
        logging.info(f"{protocol.upper()} account created successfully for {email}.")

        return account_id
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

def get_available_inboxes(email, password, protocol, server, port):
    if protocol.lower() == "imap":
        try:
            client = imaplib.IMAP4_SSL(server, int(port))
            client._mode_utf8()
            client.login(email, password)
            _, mailboxes = client.list()
            available_inboxes = [mailbox.decode().split('"')[-1] for mailbox in mailboxes]
            client.logout()
            return available_inboxes
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort) as e:
            raise e
    else:
        return []

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
                logging.info("No accounts found. Waiting for 30 seconds before the next archiving cycle.")
                conn.close()
                time.sleep(30)
                continue
            
            for account in accounts:
                account_id, email, encrypted_password, protocol, server, port, mailbox, available_inboxes, selected_inboxes, interval = account
                fetch_and_archive_emails(
                    conn,
                    account_id,
                    protocol,
                    server,
                    port,
                    email,
                    encrypted_password,
                    selected_inboxes if selected_inboxes else available_inboxes,
                )
                logging.info(f"Email archiving completed for account {account_id}. Waiting for {interval} seconds before processing the next account.")
                time.sleep(interval)  # Wait for the specified interval before processing the next account
            
            conn.close()
            logging.info("Email archiving cycle completed.")
        except Exception as e:
            logging.error(f"An error occurred during email archiving: {str(e)}")
            logging.error(f"Exception details: {traceback.format_exc()}")
            time.sleep(300)  # Wait for 5 minutes before retrying in case of an error
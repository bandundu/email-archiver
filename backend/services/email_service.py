# Services are used to interact with the database, perform business logic and other necesarry core functions. They are to be imported into the routes. Services should not use FastAPI's Request and Response classes. They should only return data to the routes. The routes will then use this data to return a response to the client.

from models.database import get_db
from models.models import Account, Email, EmailUID, Attachment
import imaplib
import poplib
import logging
import email
import hashlib
import time
import traceback
from utils.encryption import cipher_suite
from jwt import InvalidTokenError
from utils.email_utils import decode_header, extract_body, decode_filename, parse_date
import re
from config.config import config
from sqlalchemy.exc import IntegrityError

from api.routes.utilities import format_date


logger = logging.getLogger(__name__)


def fetch_and_archive_emails(
    account_id,
    protocol,
    server,
    port,
    username,
    encrypted_password,
    selected_inboxes=None,
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

        db = next(get_db())

        last_uid = (
            db.query(EmailUID.uid)
            .filter(EmailUID.account_id == account_id)
            .order_by(EmailUID.id.desc())
            .first()
        )

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
                    logging.debug(f"Selecting {inbox} for email retrieval.")

                    # strip the inbox name of any leading or trailing whitespaces
                    inbox = inbox.strip()

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
                        _, data = client.uid(
                            "fetch", ",".join(email_uids_str), "(BODY.PEEK[])"
                        )
                        raw_emails = []
                        for item in data:
                            if isinstance(item, tuple) and len(item) > 1:
                                raw_emails.append(item[1])
                    else:
                        raw_emails = []

                    total_emails = len(email_uids)
                    logging.info(
                        f"Found {total_emails} new emails for account {account_id} in inbox {inbox}."
                    )

                    skipped_emails = 0
                    failed_emails = 0
                    total_attachments_inserted = 0
                    new_emails_inserted = 0

                    for uid, raw_email in zip(email_uids, raw_emails):
                        if not raw_email:
                            logging.warning(
                                f"Failed to fetch email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} in inbox {inbox}."
                            )
                            failed_emails += 1
                            continue

                        email_message = email.message_from_bytes(raw_email)

                        subject = decode_header(email_message["Subject"])
                        sender = decode_header(email_message["From"])
                        recipients = decode_header(email_message["To"])
                        date = email_message["Date"]
                        message_id = email_message["Message-ID"]

                        fingerprint_data = (
                            f"{subject}|{sender}|{recipients}|{date}|{message_id}"
                        )
                        fingerprint = hashlib.sha256(
                            fingerprint_data.encode()
                        ).hexdigest()

                        existing_email = (
                            db.query(Email.id)
                            .filter(Email.fingerprint == fingerprint)
                            .first()
                        )
                        if existing_email:
                            logging.debug(
                                f"Skipping email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} in inbox {inbox} as it already exists."
                            )
                            skipped_emails += 1
                            continue

                        body = extract_body(email_message)
                        parsed_date = parse_date(date)

                        email_obj = Email(
                            account_id=account_id,
                            subject=subject,
                            sender=sender,
                            recipients=recipients,
                            date=parsed_date,
                            body=body,
                            fingerprint=fingerprint,
                        )
                        db.add(email_obj)
                        db.commit()

                        email_id = email_obj.id
                        new_emails_inserted += 1

                        attachments_inserted = 0
                        for part in email_message.walk():
                            if (
                                part.get_content_maintype() == "multipart"
                                or part.get("Content-Disposition") is None
                            ):
                                continue

                            filename = decode_filename(part.get_filename())
                            if filename:
                                content = part.get_payload(decode=True)
                                cid = part.get(
                                    "Content-ID", ""
                                )  # Get the Content-ID (cid) value
                                attachment = Attachment(
                                    email_id=email_id,
                                    filename=filename,
                                    content=content,
                                    cid=cid,
                                )
                                db.add(attachment)
                                attachments_inserted += 1

                        db.commit()
                        logging.info(
                            f"Inserted email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} in inbox {inbox} into the database."
                        )

                        if attachments_inserted > 0:
                            logging.info(
                                f"Saved {attachments_inserted} attachment(s) for email with UID {uid.decode() if isinstance(uid, bytes) else uid} and account {account_id} in inbox {inbox}."
                            )
                            total_attachments_inserted += attachments_inserted

                    if uidnext:
                        email_uid = EmailUID(account_id=account_id, uid=uidnext)
                        db.merge(email_uid)
                        db.commit()

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
                    logging.warning(
                        f"Failed to fetch email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id}."
                    )
                    failed_emails += 1
                    continue

                email_message = email.message_from_bytes(raw_email)

                subject = decode_header(email_message["Subject"])
                sender = decode_header(email_message["From"])
                recipients = decode_header(email_message["To"])
                date = email_message["Date"]
                message_id = email_message["Message-ID"]

                fingerprint_data = (
                    f"{subject}|{sender}|{recipients}|{date}|{message_id}"
                )
                fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

                existing_email = (
                    db.query(Email.id).filter(Email.fingerprint == fingerprint).first()
                )
                if existing_email:
                    logging.debug(
                        f"Skipping email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} as it already exists."
                    )
                    skipped_emails += 1
                    continue

                body = extract_body(email_message)
                parsed_date = parse_date(date)

                email_obj = Email(
                    account_id=account_id,
                    subject=subject,
                    sender=sender,
                    recipients=recipients,
                    date=parsed_date,
                    body=body,
                    fingerprint=fingerprint,
                )
                db.add(email_obj)
                db.commit()

                email_id = email_obj.id
                new_emails_inserted += 1

                attachments_inserted = 0
                for part in email_message.walk():
                    if (
                        part.get_content_maintype() == "multipart"
                        or part.get("Content-Disposition") is None
                    ):
                        continue

                    filename = decode_filename(part.get_filename())
                    if filename:
                        content = part.get_payload(decode=True)
                        cid = part.get(
                            "Content-ID", ""
                        )  # Get the Content-ID (cid) value
                        attachment = Attachment(
                            email_id=email_id,
                            filename=filename,
                            content=content,
                            cid=cid,
                        )
                        db.add(attachment)
                        attachments_inserted += 1

                db.commit()
                logging.info(
                    f"Inserted email with UID {uid.decode() if isinstance(uid, bytes) else uid} for account {account_id} into the database."
                )

                if attachments_inserted > 0:
                    logging.info(
                        f"Saved {attachments_inserted} attachment(s) for email with UID {uid.decode() if isinstance(uid, bytes) else uid} and account {account_id}."
                    )
                    total_attachments_inserted += attachments_inserted

        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        elapsed_time_str = f"{minutes:02d}:{seconds:02d}"

        logging.info(
            f"Email archiving completed successfully for account {account_id}."
        )
        logging.info(f"Execution time: {elapsed_time_str}")
        logging.info(f"Total emails found: {total_emails}")
        logging.info(f"Skipped emails (already exists): {skipped_emails}")
        logging.info(f"Failed emails (fetching error): {failed_emails}")
        logging.info(f"New emails inserted: {new_emails_inserted}")
        logging.info(f"New attachments saved: {total_attachments_inserted}")
        logging.info("-" * 50)

        return new_emails_inserted

    except Exception as e:
        logging.error(
            f"An error occurred during email archiving for account {account_id}: {str(e)}"
        )
        logging.error(f"Exception details: {traceback.format_exc()}")
        return 0


def create_account(
    email, password, protocol, server, port, update_interval=300, selected_inboxes=None
):
    logging.info(f"Creating {protocol.upper()} account for {email}.")

    # Ensure that the selected_inboxes list has no leading/trailing whitespaces
    if selected_inboxes:
        selected_inboxes = [inbox.strip() for inbox in selected_inboxes]

    try:
        encrypted_password = cipher_suite.encrypt(password.encode())

        db = next(get_db())  # Get a database session

        account = Account(
            email=email,
            password=encrypted_password,
            protocol=protocol,
            server=server,
            port=int(port),
            selected_inboxes=",".join(selected_inboxes) if selected_inboxes else None,
            update_interval=update_interval,
        )

        db.add(account)
        db.commit()

        account_id = account.id
        logging.info(f"{protocol.upper()} account created successfully for {email}.")

        return account_id

    except IntegrityError:
        logging.warning(
            f"{protocol.upper()} account with email {email} already exists in the database."
        )
        print(
            f"An account with email {email} already exists. Please use a different email."
        )
        return None


def read_accounts():
    db = next(get_db())
    logging.info("Fetching all IMAP/POP3 accounts from the database.")
    accounts = db.query(Account).all()
    logging.info(f"Retrieved {len(accounts)} IMAP/POP3 accounts from the database.")
    return accounts


def get_available_inboxes(email, password, protocol, server, port):
    if protocol.lower() == "imap":
        try:
            client = imaplib.IMAP4_SSL(server, int(port))
            client._mode_utf8()
            client.login(email, password)
            _, mailboxes = client.list()
            available_inboxes = [
                mailbox.decode().split('"')[-1] for mailbox in mailboxes
            ]
            client.logout()
            # Clean available inboxes for empty strings
            available_inboxes = [inbox for inbox in available_inboxes if inbox]
            return available_inboxes
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort) as e:
            raise e
    else:
        return []


# get availabl inboxes from database
def get_available_inboxes_from_db(conn, account_id):
    cursor = conn.cursor()
    cursor.execute("SELECT selected_inboxes FROM accounts WHERE id = ?", (account_id,))
    selected_inboxes = cursor.fetchone()
    if selected_inboxes:
        return selected_inboxes[0].split(",") if selected_inboxes[0] else []
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


def update_account(
    conn, account_id, email, password, protocol, server, port, mailbox, interval
):
    logging.info(f"Updating account {account_id} with email {email}.")

    # Encrypt the new password
    encrypted_password = cipher_suite.encrypt(password.encode())

    cursor = conn.cursor()
    cursor.execute(
        """UPDATE accounts
                      SET email = ?, password = ?, protocol = ?, server = ?, port = ?, mailbox = ?, interval = ?
                      WHERE id = ?""",
        (
            email,
            encrypted_password,
            protocol,
            server,
            port,
            mailbox,
            interval,
            account_id,
        ),
    )
    conn.commit()
    logging.info(f"Account {account_id} updated successfully.")


def delete_account(account_id):
    db = next(get_db())
    logging.info(f"Deleting account {account_id}.")
    account = db.query(Account).filter(Account.id == account_id).first()
    if account:
        db.delete(account)
        db.commit()
        logging.info(f"Account {account_id} deleted successfully.")


def delete_email(email_id: int):
    db = next(get_db())

    try:
        email = db.query(Email).filter(Email.id == email_id).first()
        if email:
            db.delete(email)
            db.query(Attachment).filter(Attachment.email_id == email_id).delete()
            db.commit()
            return {"message": "Email deleted successfully"}
        else:
            return {"error": "Email not found"}

    except Exception as e:
        db.rollback()
        return {"error": "An error occurred while deleting the email"}


def export_email(email_id):
    db = next(get_db())
    email = db.query(Email).filter(Email.id == email_id).first()

    if email:
        email_data = email.body  # Assuming the body column contains the raw email data
        return email_data
    else:
        return None


def get_emails(
    page: int = 1, per_page: int = 10, sort_by: str = "date", sort_order: str = "desc"
):
    db = next(get_db())

    total_emails = db.query(Email).count()

    offset = (page - 1) * per_page

    emails = (
        db.query(Email)
        .order_by(getattr(getattr(Email, sort_by), sort_order)())
        .limit(per_page)
        .offset(offset)
        .all()
    )

    email_data = []
    for email in emails:
        attachment_count = (
            db.query(Attachment).filter(Attachment.email_id == email.id).count()
        )

        email_data.append(
            {
                "id": email.id,
                "account_id": email.account_id,
                "subject": email.subject,
                "sender": email.sender,
                "recipients": email.recipients,
                "date": str(email.date),  # Convert the date to a string for FastAPI
                "body": email.body,
                "unique_id": email.fingerprint,
                "has_attachments": attachment_count > 0,
            }
        )

    return {"emails": email_data, "total_emails": total_emails}


def email_details(email_id: int):
    db = next(get_db())
    email, attachments, attachment_filenames = get_email_details(db, email_id)

    if email:
        email_data = {
            "id": email.id,
            "account_id": email.account_id,
            "subject": email.subject,
            "sender": email.sender,
            "recipients": email.recipients,
            "date": str(email.date),  # Convert the date to a string for FastAPI
            "body": email.body,
            "content_type": email.content_type,
        }

        attachment_data = [
            {"id": attachment.id, "filename": attachment.filename}
            for attachment in attachments
        ]

        # Check if the email body is large
        body_size = len(email.body)
        is_large_file = body_size > 1000000  # Adjust the threshold as needed

        return {
            "email": email_data,
            "attachments": attachment_data,
            "is_large_file": is_large_file,
        }
    else:
        return {"error": "Email not found"}


def latest_emails(limit=5):
    db = next(get_db())

    latest_emails = (
        db.query(Email.subject, Email.sender, Email.date)
        .order_by(Email.date.desc())
        .limit(limit)
        .all()
    )

    emails_data = [
        {
            "subject": email.subject,
            "sender": email.sender,
            "date": format_date(email.date),
        }
        for email in latest_emails
    ]

    return emails_data


def get_email_details(email_id):
    logging.info(f"Fetching email details for email ID {email_id}.")

    db = next(get_db())  # Get a database session

    email = db.query(Email).filter(Email.id == email_id).first()

    if email:
        attachments = db.query(Attachment).filter(Attachment.email_id == email_id).all()

        html_tags = re.compile(r"<(?!!)(?P<tag>[a-zA-Z]+).*?>", re.IGNORECASE)
        code_block_pattern = re.compile(r"```.*?```", re.DOTALL)

        content_type = "text/plain"
        body = email.body

        # Check for HTML content
        if (
            "<!doctype html>" in body.lower()
            or "<html" in body.lower()
            or html_tags.search(body) is not None
        ):
            content_type = "text/html"
            logging.info(f"Email with ID {email_id} is an HTML email.")

            # Replace code blocks with <pre><code> tags
            body = code_block_pattern.sub(
                lambda match: f"<pre><code>{match.group()[3:-3]}</code></pre>", body
            )

            # Extract the HTML portion of the email
            html_start = (
                body.lower().find("<!doctype html>")
                if "<!doctype html>" in body.lower()
                else body.lower().find("<html")
            )
            html_end = body.lower().rfind("</html>") + len("</html>")
            if html_start != -1 and html_end != -1:
                body = body[html_start:html_end]
        else:
            logging.info(f"Email with ID {email_id} is a plain text email.")

            # Replace code blocks with <pre><code> tags
            body = code_block_pattern.sub(
                lambda match: f"<pre><code>{match.group()[3:-3]}</code></pre>", body
            )

        attachment_data = [
            {"id": attachment.id, "filename": attachment.filename}
            for attachment in attachments
        ]

        # Check if the email body is large
        body_size = len(email.body)
        is_large_file = body_size > 1000000

        email_data = {
            "id": email.id,
            "account_id": email.account_id,
            "subject": email.subject,
            "sender": email.sender,
            "recipients": email.recipients,
            "date": str(email.date),
            "body": body,
            "content_type": content_type,
        }

        logging.info(
            f"Email details and attachments fetched successfully for email ID {email_id}."
        )

        return {
            "email": email_data,
            "attachments": attachment_data,
            "is_large_file": is_large_file,
        }
    else:
        logging.warning(f"Email with ID {email_id} not found.")
        return {"error": "Email not found"}

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

# Load environment variables from .env file
load_dotenv()

# Load the secret key from the environment variable
secret_key = os.environ.get('SECRET_KEY').encode()
# In email_archiver.py
cipher_suite = Fernet(secret_key)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_database():
    db_exists = os.path.exists('email_archive.db')
    if not db_exists:
        # Connect to the database. This will create the file if it does not exist.
        conn = sqlite3.connect('email_archive.db')
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           email TEXT UNIQUE,
                           password TEXT,
                           protocol TEXT,
                           server TEXT,
                           port INTEGER,
                           mailbox TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS emails
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           account_id INTEGER,
                           subject TEXT,
                           sender TEXT,
                           recipients TEXT,
                           date DATETIME,
                           body TEXT,
                           unique_id TEXT,
                           FOREIGN KEY (account_id) REFERENCES accounts (id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS attachments
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           email_id INTEGER,
                           filename TEXT,
                           content BLOB,
                           FOREIGN KEY (email_id) REFERENCES emails (id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS email_uids
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           account_id INTEGER,
                           uid TEXT,
                           FOREIGN KEY (account_id) REFERENCES accounts (id))''')
        
        # Commit changes and close the connection
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    else:
        logging.info("Database already exists.")
                   

DEFAULT_PROTOCOL = 'pop3'  # Use POP3 as the default protocol

def parse_date(date_str):
    if date_str is None:
        return None
    try:
        date_tuple = parsedate_to_datetime(date_str)
        return date_tuple.strftime('%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError):
        return None
    
def fetch_and_archive_emails(conn, account_id, protocol, server, port, username, encrypted_password, mailbox=None):
    try:
        logging.info(f"Started email archiving for account {account_id}.")
        if not isinstance(encrypted_password, bytes):
            encrypted_password = encrypted_password.encode()
        # In email_archiver.py, in the fetch_and_archive_emails function
        try:
            password = cipher_suite.decrypt(encrypted_password).decode()
        except InvalidTokenError as e:
            print("Decryption Error:", str(e))
        if protocol == 'imap':
            # Connect to the IMAP server
            client = imaplib.IMAP4_SSL(server, port)
            client._mode_utf8() 
            client.login(username, password)
            
            # Select the mailbox to fetch emails from
            client.select(mailbox, readonly=True)
            
            # Fetch email UIDs
            _, data = client.uid('search', None, 'ALL')
            email_uids = data[0].split()
        elif protocol == 'pop3':
            # Connect to the POP3 server
            client = poplib.POP3_SSL(server, port)
            client.user(username)
            client.pass_(password)
            
            # Get the number of emails
            num_emails = len(client.list()[1])
            email_uids = range(1, num_emails + 1)
        
        logging.info(f"Found {len(email_uids)} emails for account {account_id}.")
        
        cursor = conn.cursor()
        
        for uid in email_uids:
            logging.debug(f"Processing email with UID {uid} for account {account_id}.")
            
            if protocol == 'imap':
                # Fetch the email content using IMAP
                _, data = client.uid('fetch', uid, '(RFC822)')
                raw_email = data[0][1]
            elif protocol == 'pop3':
                # Fetch the email content using POP3
                raw_email = b'\n'.join(client.retr(uid)[1])
            
            # Parse the email content
            email_message = email.message_from_bytes(raw_email)
            
            # Extract email metadata
            subject_parts = email.header.decode_header(email_message['Subject'])
            decoded_subject_parts = []
            for part, encoding in subject_parts:
                if isinstance(part, bytes):
                    decoded_subject_parts.append(part.decode(encoding or 'utf-8'))
                else:
                    decoded_subject_parts.append(part)
            subject = ''.join(decoded_subject_parts)

            sender_parts = email.header.decode_header(email_message['From'])
            decoded_sender_parts = []
            for part, encoding in sender_parts:
                if isinstance(part, bytes):
                    decoded_sender_parts.append(part.decode(encoding or 'utf-8'))
                else:
                    decoded_sender_parts.append(part)
            sender = ''.join(decoded_sender_parts)

            recipients_parts = email.header.decode_header(email_message['To'])
            decoded_recipients_parts = []
            for part, encoding in recipients_parts:
                if isinstance(part, bytes):
                    decoded_recipients_parts.append(part.decode(encoding or 'utf-8'))
                else:
                    decoded_recipients_parts.append(part)
            recipients = ''.join(decoded_recipients_parts)

            date = email_message['Date']
            message_id = email_message['Message-ID']
            
            # Create a unique identifier for the email
            if protocol == 'imap':
                unique_id = str(uid)
            elif protocol == 'pop3':
                unique_id = f"{message_id}_{date}_{sender}_{subject}"
            
            # Check if the email already exists in the database
            cursor.execute("SELECT id FROM emails WHERE unique_id = ?", (unique_id,))
            existing_email = cursor.fetchone()
            if existing_email:
                logging.debug(f"Skipping email with UID {uid} for account {account_id} as it already exists.")
                continue  # Skip archiving if the email already exists
            
            # Extract email body
            body = ''
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain' or content_type == 'text/html':
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset()
                        if charset:
                            body += payload.decode(charset, errors='replace')
                        else:
                            body += payload.decode(errors='replace')
            else:
                payload = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset()
                if charset:
                    body = payload.decode(charset, errors='replace')
                else:
                    body = payload.decode(errors='replace')
            
            # Insert email metadata into the database
            parsed_date = parse_date(date)
            cursor.execute('''INSERT INTO emails (account_id, subject, sender, recipients, date, body, unique_id)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', (account_id, subject, sender, recipients, parsed_date, body, unique_id))
            email_id = cursor.lastrowid
            
            logging.info(f"Inserted email with UID {uid} for account {account_id} into the database.")
            
            # Save attachments
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    filename_parts = email.header.decode_header(filename)
                    decoded_filename_parts = []
                    for filename_part, encoding in filename_parts:
                        if isinstance(filename_part, bytes):
                            decoded_filename_parts.append(filename_part.decode(encoding or 'utf-8'))
                        else:
                            decoded_filename_parts.append(filename_part)
                    filename = ''.join(decoded_filename_parts)
                    
                    logging.info(f"Found attachment {filename} for email with UID {uid} for account {account_id}.")
                    content = part.get_payload(decode=True)
                    cursor.execute('''INSERT INTO attachments (email_id, filename, content)
                                    VALUES (?, ?, ?)''', (email_id, filename, content))
                    
                    logging.info(f"Saved attachment {filename} for email with UID {uid} for account {account_id}.")
                    
        conn.commit()
        
        # Close the connection
        if protocol == 'imap':
            client.close()
            client.logout()
        elif protocol == 'pop3':
            client.quit()
        
        logging.info(f"Email archiving completed successfully for account {account_id}.")
    
    except Exception as e:
        logging.error(f"An error occurred during email archiving for account {account_id}: {str(e)}")
        logging.error(f"Exception details: {traceback.format_exc()}")

def create_account(conn, email, password, protocol, server, port):
    logging.info(f"Creating {protocol.upper()} account for {email}.")
    mailbox = 'INBOX' if protocol == 'imap' else None
    
    try:
        if protocol == 'imap':
            client = imaplib.IMAP4_SSL(server, int(port))
            client._mode_utf8() 
            client.login(email, password)
            client.logout()
        elif protocol == 'pop3':
            client = poplib.POP3_SSL(server, int(port))
            client.user(email)
            client.pass_(password)
            client.quit()
        
        # Encrypt the password
        encrypted_password = cipher_suite.encrypt(password.encode())
        
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO accounts (email, password, protocol, server, port, mailbox)
                          VALUES (?, ?, ?, ?, ?, ?)''', (email, encrypted_password, protocol, server, int(port), mailbox))
        account_id = cursor.lastrowid
        conn.commit()
        logging.info(f"{protocol.upper()} account created successfully for {email}.")
        
        # Run email archiving for the newly created account
        run_archiver_once(account_id)
        
        return account_id
    except (imaplib.IMAP4.error, poplib.error_proto) as e:
        logging.error(f"Failed to create {protocol.upper()} account for {email}. Error: {str(e)}")
        print(f"Failed to create {protocol.upper()} account. Please check the {protocol.upper()} server and port manually.")
        return None
    except sqlite3.IntegrityError:
        logging.warning(f"{protocol.upper()} account with email {email} already exists in the database.")
        print(f"An account with email {email} already exists. Please use a different email.")
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
        logging.info(f"Account details fetched successfully for account ID {account_id}.")
        return account
    else:
        logging.warning(f"Account with ID {account_id} not found.")
        return None

def update_account(conn, account_id, email, password, protocol, server, port, mailbox):
    logging.info(f"Updating account {account_id} with email {email}.")
    
    # Encrypt the new password
    encrypted_password = cipher_suite.encrypt(password.encode())
    
    cursor = conn.cursor()
    cursor.execute('''UPDATE accounts
                      SET email = ?, password = ?, protocol = ?, server = ?, port = ?, mailbox = ?
                      WHERE id = ?''', (email, encrypted_password, protocol, server, port, mailbox, account_id))
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
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for email in emails:
            email_id = email[0]
            email_data = email[-1]  # Assuming the last column contains the raw email data
            zip_file.writestr(f"email_{email_id}.eml", email_data)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def export_search_results(conn, query):
    emails = search_emails(conn, query)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for email in emails:
            email_id = email[0]
            email_data = email[-1]  # Assuming the last column contains the raw email data
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
    date_range_pattern = r'(\d{1,2}\s+\w{3}\s+\d{4})\s*-\s*(\d{1,2}\s+\w{3}\s+\d{4})'
    date_range_match = re.search(date_range_pattern, query)

    if date_range_match:
        start_date_str, end_date_str = date_range_match.groups()
        try:
            start_date = parser.parse(start_date_str, fuzzy=True).strftime('%Y-%m-%d')
            end_date = parser.parse(end_date_str, fuzzy=True).strftime('%Y-%m-%d')
            cursor.execute("SELECT * FROM emails WHERE date BETWEEN ? AND ?", (start_date, end_date))
            emails = cursor.fetchall()
            logging.info(f"Found {len(emails)} emails within the date range.")
            return emails
        except (ValueError, TypeError):
            logging.info("Invalid date range format. Proceeding with normal search.")
    else:
        # Check if the query is a valid date string
        try:
            query_date = parser.parse(query, fuzzy=True)
            date_query = query_date.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            date_query = None

        if date_query:
            # Search emails by date (case-insensitive)
            cursor.execute("SELECT * FROM emails WHERE LOWER(date) LIKE ?", (f"%{date_query}%",))
        else:
            # Split the query into individual terms
            query_terms = re.findall(r'\b\w+\b', query)

            # Check if there are any valid search terms
            if not query_terms:
                logging.info("No valid search terms found. Returning no results.")
                return []  # Return an empty list

            # Build the SQL query dynamically based on the number of query terms
            sql_query = "SELECT * FROM emails WHERE "
            sql_conditions = []
            sql_params = []

            for term in query_terms:
                sql_conditions.append("(LOWER(subject) LIKE ? OR LOWER(sender) LIKE ? OR LOWER(recipients) LIKE ? OR LOWER(body) LIKE ?)")
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
    
    cursor.execute("SELECT *, (SELECT GROUP_CONCAT(filename) FROM attachments WHERE email_id = emails.id) AS attachment_filenames FROM emails WHERE id = ?", (email_id,))
    email = cursor.fetchone()
    
    cursor.execute("SELECT id, filename FROM attachments WHERE email_id = ?", (email_id,))
    attachments = cursor.fetchall()
    
    html_tags = re.compile(r'<(?!!)(?P<tag>[a-zA-Z]+).*?>', re.IGNORECASE)
    code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
    
    if email:
        content_type = 'text/plain'
        logging.info(f"Email with ID {email_id} is a plain text email.")
        
        if '<!doctype html>' in email[6].lower() or '<html' in email[6].lower() or html_tags.search(email[6]) is not None:
            content_type = 'text/html'
            logging.info(f"Email with ID {email_id} is an HTML email.")
            
            # Replace code blocks with <pre><code> tags
            body = code_block_pattern.sub(lambda match: f'<pre><code>{match.group()[3:-3]}</code></pre>', email[6])
            
            # Extract the HTML portion of the email
            html_start = body.lower().find('<!doctype html>') if '<!doctype html>' in body.lower() else body.lower().find('<html')
            html_end = body.lower().rfind('</html>') + len('</html>')
            if html_start != -1 and html_end != -1:
                email = email[:6] + (body[html_start:html_end], content_type) + (email[-1],)
            else:
                email = email[:6] + (body, content_type) + (email[-1],)
        else:
            # Replace code blocks with <pre><code> tags
            body = code_block_pattern.sub(lambda match: f'<pre><code>{match.group()[3:-3]}</code></pre>', email[6])
            email = email[:6] + (body, content_type) + (email[-1],)
        
        attachment_filenames = email[-1].split(',') if email[-1] else []
        logging.info(f"Email details and attachments fetched successfully for email ID {email_id}.")
        return email, attachments, attachment_filenames
    
    else:
        logging.warning(f"Email with ID {email_id} not found.")
        return None, None, None

def run_archiver_once(account_id):
    try:
        logging.info(f"Starting email archiving for account {account_id}...")
        conn = sqlite3.connect('email_archive.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        if account:
            account_id, email, encrypted_password, protocol, server, port, mailbox = account
            fetch_and_archive_emails(conn, account_id, protocol, server, port, email, encrypted_password, mailbox)
        else:
            logging.warning(f"Account with ID {account_id} not found.")
        conn.close()
        logging.info(f"Email archiving completed for account {account_id}.")
    except Exception as e:
        logging.error(f"An error occurred during email archiving for account {account_id}: {str(e)}")
        logging.error(f"Exception details: {traceback.format_exc()}")

def run_archiver():
    while True:
        try:
            logging.info("Starting email archiving cycle...")
            conn = sqlite3.connect('email_archive.db')
            accounts = read_accounts(conn)
            for account in accounts:
                account_id, email, encrypted_password, protocol, server, port, mailbox = account
                fetch_and_archive_emails(conn, account_id, protocol, server, port, email, encrypted_password, mailbox)
            conn.close()
            logging.info("Email archiving cycle completed.")
            time.sleep(300)  # Wait for 5 minutes before the next archiving cycle
        except Exception as e:
            logging.error(f"An error occurred during email archiving: {str(e)}")
            time.sleep(300)  # Wait for 5 minutes before retrying
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Email Archiver CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # IMAP/POP3 Account Management
    parser_create_account = subparsers.add_parser('create_account', help='Create a new IMAP/POP3 account')
    parser_create_account.add_argument('email', help='Email address')
    parser_create_account.add_argument('password', help='Email password')
    parser_create_account.add_argument('--protocol', choices=['imap', 'pop3'], help='Email protocol (imap or pop3)', default=DEFAULT_PROTOCOL)

    parser_list_accounts = subparsers.add_parser('list_accounts', help='List all IMAP/POP3 accounts')

    parser_update_account = subparsers.add_parser('update_account', help='Update an IMAP/POP3 account')
    parser_update_account.add_argument('account_id', type=int, help='Account ID')
    parser_update_account.add_argument('email', help='Email address')
    parser_update_account.add_argument('password', help='Email password')
    parser_update_account.add_argument('protocol', choices=['imap', 'pop3'], help='Email protocol (imap or pop3)')
    parser_update_account.add_argument('server', help='Email server')
    parser_update_account.add_argument('port', type=int, help='Email server port')
    parser_update_account.add_argument('mailbox', help='Mailbox to archive (IMAP only)')

    parser_delete_account = subparsers.add_parser('delete_account', help='Delete an IMAP/POP3 account')
    parser_delete_account.add_argument('account_id', type=int, help='Account ID')

    # Email Archive
    parser_search_emails = subparsers.add_parser('search_emails', help='Search for emails')
    parser_search_emails.add_argument('query', help='Search query')

    parser_get_email = subparsers.add_parser('get_email', help='Get email details')
    parser_get_email.add_argument('email_id', type=int, help='Email ID')

    # Archiver
    parser_run_archiver = subparsers.add_parser('run_archiver', help='Run the email archiver')

    args = parser.parse_args()

    logging.info(f"Executing command: {args.command}")

    if args.command == 'create_account':
        create_account(args.email, args.password, args.protocol)
    elif args.command == 'list_accounts':
        accounts = read_accounts()
        for account in accounts:
            print(account)
    elif args.command == 'update_account':
        update_account(args.account_id, args.email, args.password, args.protocol, args.server, args.port, args.mailbox)
    elif args.command == 'delete_account':
        delete_account(args.account_id)
    elif args.command == 'search_emails':
        emails = search_emails(args.query)
        for email in emails:
            print(email)
    elif args.command == 'get_email':
        email, attachments = get_email_details(args.email_id)
        if email:
            print(email)
            print("Attachments:")
            for attachment in attachments:
                print(attachment)
        else:
            print(f"Email with ID {args.email_id} not found.")
    elif args.command == 'run_archiver':
        run_archiver()

    logging.info(f"Command {args.command} executed successfully.")

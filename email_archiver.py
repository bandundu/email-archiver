import argparse
import imaplib
import email
import sqlite3
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database connection
conn = sqlite3.connect('email_archive.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS imap_accounts
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT,
                   password TEXT,
                   imap_server TEXT,
                   imap_port INTEGER,
                   mailbox TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS emails
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   account_id INTEGER,
                   subject TEXT,
                   sender TEXT,
                   recipients TEXT,
                   date TEXT,
                   body TEXT,
                   FOREIGN KEY (account_id) REFERENCES imap_accounts (id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS attachments
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   email_id INTEGER,
                   filename TEXT,
                   content BLOB,
                   FOREIGN KEY (email_id) REFERENCES emails (id))''')

def fetch_and_archive_emails(account_id, imap_server, imap_port, username, password, mailbox):
    try:
        # Connect to the email server
        imap = imaplib.IMAP4_SSL(imap_server, imap_port)
        imap.login(username, password)
        
        # Select the mailbox to fetch emails from
        imap.select(mailbox)
        
        # Fetch email UIDs
        _, data = imap.uid('search', None, 'ALL')
        email_uids = data[0].split()
        
        for uid in email_uids:
            # Fetch the email content
            _, data = imap.uid('fetch', uid, '(RFC822)')
            raw_email = data[0][1]
            
            # Parse the email content
            email_message = email.message_from_bytes(raw_email)
            
            # Extract email metadata
            subject = email_message['Subject']
            sender = email_message['From']
            recipients = email_message['To']
            date = email_message['Date']
            
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
            cursor.execute('''INSERT INTO emails (account_id, subject, sender, recipients, date, body)
                              VALUES (?, ?, ?, ?, ?, ?)''', (account_id, subject, sender, recipients, date, body))
            email_id = cursor.lastrowid
            
            # Save attachments
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    content = part.get_payload(decode=True)
                    cursor.execute('''INSERT INTO attachments (email_id, filename, content)
                                      VALUES (?, ?, ?)''', (email_id, filename, content))
        
        # Commit the changes
        conn.commit()
        
        # Close the IMAP connection
        imap.close()
        imap.logout()
        
        logging.info(f"Email archiving completed for account {account_id}.")
    
    except Exception as e:
        logging.error(f"An error occurred for account {account_id}: {str(e)}")

def create_imap_account(username, password, imap_server, imap_port, mailbox):
    cursor.execute('''INSERT INTO imap_accounts (username, password, imap_server, imap_port, mailbox)
                      VALUES (?, ?, ?, ?, ?)''', (username, password, imap_server, imap_port, mailbox))
    conn.commit()
    logging.info(f"IMAP account created for {username}.")

def read_imap_accounts():
    cursor.execute("SELECT * FROM imap_accounts")
    return cursor.fetchall()

def update_imap_account(account_id, username, password, imap_server, imap_port, mailbox):
    cursor.execute('''UPDATE imap_accounts
                      SET username = ?, password = ?, imap_server = ?, imap_port = ?, mailbox = ?
                      WHERE id = ?''', (username, password, imap_server, imap_port, mailbox, account_id))
    conn.commit()
    logging.info(f"IMAP account {account_id} updated.")

def delete_imap_account(account_id):
    cursor.execute("DELETE FROM imap_accounts WHERE id = ?", (account_id,))
    conn.commit()
    logging.info(f"IMAP account {account_id} deleted.")

def search_emails(query):
    cursor.execute("SELECT * FROM emails WHERE subject LIKE ? OR sender LIKE ? OR recipients LIKE ? OR body LIKE ?",
                   (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
    return cursor.fetchall()

def get_email_details(email_id):
    cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
    email = cursor.fetchone()
    if email:
        cursor.execute("SELECT * FROM attachments WHERE email_id = ?", (email_id,))
        attachments = cursor.fetchall()
        return email, attachments
    return None, None

def run_archiver():
    while True:
        accounts = read_imap_accounts()
        for account in accounts:
            account_id, username, password, imap_server, imap_port, mailbox = account
            fetch_and_archive_emails(account_id, imap_server, imap_port, username, password, mailbox)
        time.sleep(300)  # Wait for 5 minutes before the next archiving cycle

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Email Archiver CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # IMAP Account Management
    parser_create_account = subparsers.add_parser('create_account', help='Create a new IMAP account')
    parser_create_account.add_argument('username', help='IMAP account username')
    parser_create_account.add_argument('password', help='IMAP account password')
    parser_create_account.add_argument('imap_server', help='IMAP server')
    parser_create_account.add_argument('imap_port', type=int, help='IMAP port')
    parser_create_account.add_argument('mailbox', help='Mailbox to archive')

    parser_list_accounts = subparsers.add_parser('list_accounts', help='List all IMAP accounts')

    parser_update_account = subparsers.add_parser('update_account', help='Update an IMAP account')
    parser_update_account.add_argument('account_id', type=int, help='IMAP account ID')
    parser_update_account.add_argument('username', help='IMAP account username')
    parser_update_account.add_argument('password', help='IMAP account password')
    parser_update_account.add_argument('imap_server', help='IMAP server')
    parser_update_account.add_argument('imap_port', type=int, help='IMAP port')
    parser_update_account.add_argument('mailbox', help='Mailbox to archive')

    parser_delete_account = subparsers.add_parser('delete_account', help='Delete an IMAP account')
    parser_delete_account.add_argument('account_id', type=int, help='IMAP account ID')

    # Email Archive
    parser_search_emails = subparsers.add_parser('search_emails', help='Search for emails')
    parser_search_emails.add_argument('query', help='Search query')

    parser_get_email = subparsers.add_parser('get_email', help='Get email details')
    parser_get_email.add_argument('email_id', type=int, help='Email ID')

    # Archiver
    parser_run_archiver = subparsers.add_parser('run_archiver', help='Run the email archiver')

    args = parser.parse_args()

    if args.command == 'create_account':
        create_imap_account(args.username, args.password, args.imap_server, args.imap_port, args.mailbox)
    elif args.command == 'list_accounts':
        accounts = read_imap_accounts()
        for account in accounts:
            print(account)
    elif args.command == 'update_account':
        update_imap_account(args.account_id, args.username, args.password, args.imap_server, args.imap_port, args.mailbox)
    elif args.command == 'delete_account':
        delete_imap_account(args.account_id)
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
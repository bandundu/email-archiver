import argparse
import imaplib
import poplib
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
cursor.execute('''CREATE TABLE IF NOT EXISTS accounts
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   email TEXT,
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
                   date TEXT,
                   body TEXT,
                   FOREIGN KEY (account_id) REFERENCES accounts (id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS attachments
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   email_id INTEGER,
                   filename TEXT,
                   content BLOB,
                   FOREIGN KEY (email_id) REFERENCES emails (id))''')

# Domain-specific IMAP and POP3 server configurations
SERVER_CONFIGS = {
    'mupende.com': {
        'imap': ('imaps.udag.de', 993),
        'pop3': ('pops.udag.de', 995)
    },
    'gmail.com': {
        'imap': ('imap.gmail.com', 993),
        'pop3': ('pop.gmail.com', 995)
    },
    # Add more domain-specific configurations here
}

DEFAULT_PROTOCOL = 'pop3'  # Use POP3 as the default protocol

def fetch_and_archive_emails(account_id, protocol, server, port, username, password, mailbox=None):
    try:
        if protocol == 'imap':
            # Connect to the IMAP server
            client = imaplib.IMAP4_SSL(server, port)
            client.login(username, password)
            
            # Select the mailbox to fetch emails from
            client.select(mailbox)
            
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
        
        for uid in email_uids:
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
        
        # Close the connection
        if protocol == 'imap':
            client.close()
            client.logout()
        elif protocol == 'pop3':
            client.quit()
        
        logging.info(f"Email archiving completed for account {account_id}.")
    
    except Exception as e:
        logging.error(f"An error occurred for account {account_id}: {str(e)}")

def create_account(email, password, protocol=DEFAULT_PROTOCOL):
    domain = email.split('@')[1]
    if domain in SERVER_CONFIGS:
        server_config = SERVER_CONFIGS[domain]
        if protocol in server_config:
            server, port = server_config[protocol]
            mailbox = 'INBOX' if protocol == 'imap' else None
            try:
                if protocol == 'imap':
                    client = imaplib.IMAP4_SSL(server, port)
                    client.login(email, password)
                    client.logout()
                elif protocol == 'pop3':
                    client = poplib.POP3_SSL(server, port)
                    client.user(email)
                    client.pass_(password)
                    client.quit()
                
                cursor.execute('''INSERT INTO accounts (email, password, protocol, server, port, mailbox)
                                  VALUES (?, ?, ?, ?, ?, ?)''', (email, password, protocol, server, port, mailbox))
                conn.commit()
                logging.info(f"{protocol.upper()} account created for {email}.")
            except (imaplib.IMAP4.error, poplib.error_proto) as e:
                logging.error(f"Failed to create {protocol.upper()} account for {email}. Error: {str(e)}")
                print(f"Failed to create {protocol.upper()} account. Please check the {protocol.upper()} server and port manually.")
        else:
            print(f"{protocol.upper()} configuration not found for the domain {domain}.")
    else:
        print(f"Domain {domain} not found in the predefined configurations.")
        print(f"Using the default {DEFAULT_PROTOCOL.upper()} protocol.")
        create_account(email, password, DEFAULT_PROTOCOL)

def read_accounts():
    cursor.execute("SELECT * FROM accounts")
    return cursor.fetchall()

def update_account(account_id, email, password, protocol, server, port, mailbox):
    cursor.execute('''UPDATE accounts
                      SET email = ?, password = ?, protocol = ?, server = ?, port = ?, mailbox = ?
                      WHERE id = ?''', (email, password, protocol, server, port, mailbox, account_id))
    conn.commit()
    logging.info(f"Account {account_id} updated.")

def delete_account(account_id):
    cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    logging.info(f"Account {account_id} deleted.")

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
        accounts = read_accounts()
        for account in accounts:
            account_id, email, password, protocol, server, port, mailbox = account
            fetch_and_archive_emails(account_id, protocol, server, port, email, password, mailbox)
        time.sleep(300)  # Wait for 5 minutes before the next archiving cycle

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
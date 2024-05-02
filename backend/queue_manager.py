import queue
import threading
import time
import sqlite3
import logging
from email_archiver import create_account, fetch_and_archive_emails, get_account
from email_archiver import get_database_connection


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Initialize queue
task_queue = queue.Queue()

# Task types
ACCOUNT_CREATION = 'account_creation'
EMAIL_RETRIEVAL = 'email_retrieval'

def initialize_email_retrieval_tasks():
    conn = sqlite3.connect('data/email_archive.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, interval FROM accounts")
    accounts = cursor.fetchall()
    conn.close()

    for account in accounts:
        account_id, interval = account
        task_queue.put({'type': EMAIL_RETRIEVAL, 'account_id': account_id})
        logging.info(f'Added email retrieval task for account {account_id} to the queue.')

    logging.info('Email retrieval tasks initialized.')

# Function to process tasks
def process_tasks():
    while True:
        if not task_queue.empty():
            task = task_queue.get()
            task_type = task['type']

            if task_type == ACCOUNT_CREATION:
                email = task['email']
                password = task['password']
                protocol = task['protocol']
                server = task['server']
                port = task['port']
                interval = task['interval']
                selected_inboxes = task['selected_inboxes']

                conn = sqlite3.connect('data/email_archive.db')
                account_id = create_account(conn, email, password, protocol, server, port, interval, selected_inboxes)
                conn.close()

                if account_id:
                    logging.info(f'Account created successfully for {email}. Adding to email retrieval queue.')
                    task_queue.put({'type': EMAIL_RETRIEVAL, 'account_id': account_id})
                else:
                    logging.error(f'Failed to create account for {email}.')

            elif task_type == EMAIL_RETRIEVAL:
                account_id = task['account_id']
                conn = sqlite3.connect('data/email_archive.db')
                account = get_account(conn, account_id)

                if account:
                    email, encrypted_password, protocol, server, port, mailbox, available_inboxes, selected_inboxes, interval = account[1:]
                    fetch_and_archive_emails(conn, account_id, protocol, server, port, email, encrypted_password, selected_inboxes)
                    logging.info(f'Email retrieval completed for account {account_id}. Adding back to queue after {interval} seconds.')
                    task_queue.put({'type': EMAIL_RETRIEVAL, 'account_id': account_id})
                    time.sleep(interval)
                else:
                    logging.error(f'Account with ID {account_id} not found.')

                conn.close()

            task_queue.task_done()

# Initialize the database connection
conn = get_database_connection()


# Start worker thread
task_worker = threading.Thread(target=process_tasks)

# Initialize email retrieval tasks
initialize_email_retrieval_tasks()

task_worker.start()
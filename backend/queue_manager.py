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
    """
    Initialize email retrieval tasks by querying the database for existing accounts
    and adding them to the task queue.
    """
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
    """
    Continuously process tasks from the task queue based on their type.
    """
    while True:
        try:
            task = task_queue.get(timeout=60)  # Wait for a task with a timeout of 60 seconds
            task_type = task['type']
            logging.info(f'Processing task: {task_type}')

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
                    logging.info(f'Email retrieval completed for account {account_id}.')
                    task_queue.put({'type': EMAIL_RETRIEVAL, 'account_id': account_id})
                    time.sleep(interval)
                else:
                    logging.error(f'Account with ID {account_id} not found.')
                conn.close()

            task_queue.task_done()

        except queue.Empty:
            logging.info('Task queue is empty. Waiting for new tasks...')
            time.sleep(5)  # Sleep for 5 seconds before checking the queue again

# Initialize the database connection
conn = get_database_connection()


# Start worker thread
task_worker = threading.Thread(target=process_tasks)

# Initialize email retrieval tasks
initialize_email_retrieval_tasks()

task_worker.start()
# Services are used to interact with the database, perform business logic and other necesarry core functions. They are to be imported into the routes. Services should not use FastAPI's Request and Response classes. They should only return data to the routes. The routes will then use this data to return a response to the client.

# queue_manager.py is a script that manages a task queue for creating accounts and retrieving emails. It initializes the task queue with email retrieval tasks for existing accounts and processes tasks based on their execution time. The script uses a worker thread to process tasks and executes account creation and email retrieval tasks as needed.

import queue
import threading
import time
import sqlite3
import logging
from models.models import Account
from models.database import get_db
from config.config import config

import services.email_service as email_service


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize queue
task_queue = queue.Queue()

# Task types
ACCOUNT_CREATION = "account_creation"
EMAIL_RETRIEVAL = "email_retrieval"


class Task:
    def __init__(
        self,
        task_type,
        task_data,
        interval,
        next_execution=None,
        execute_immediately=False,
    ):
        self.task_type = task_type
        self.task_data = task_data
        self.interval = interval
        self.next_execution = next_execution or time.time() + interval
        self.execute_immediately = execute_immediately

    def to_dict(self):
        return {
            "task_type": self.task_type,
            "task_data": self.task_data,
            "interval": self.interval,
            "next_execution": self.next_execution,
            "execute_immediately": self.execute_immediately,
        }

    @classmethod
    def create_task(
        cls,
        task_type,
        task_data,
        interval=None,
        next_execution=None,
        execute_immediately=False,
    ):
        if interval is None and execute_immediately:
            next_execution = time.time()
        return {
            "task_type": task_type,
            "task_data": task_data,
            "interval": interval,
            "next_execution": next_execution or time.time() + (interval or 0),
            "execute_immediately": execute_immediately,
        }


def initialize_email_retrieval_tasks():
    """
    Initialize email retrieval tasks by querying the database for existing accounts
    and adding them to the task queue.
    """
    logging.info("Initializing email retrieval tasks...")
    db = next(get_db())
    accounts = db.query(Account.id, Account.update_interval).all()

    for account in accounts:
        account_id, interval = account
        task_data = {"account_id": account_id}
        task = Task.create_task(EMAIL_RETRIEVAL, task_data, interval)
        task_queue.put(task)
        logging.info(
            f"Added email retrieval task for account {account_id} to the queue."
        )

    logging.info("Email retrieval tasks initialized.")


# Function to process tasks
def process_tasks():
    while True:
        current_time = time.time()
        task = None

        try:
            task_dict = task_queue.get(block=False)
            task = Task(**task_dict)
        except queue.Empty:
            pass

        if task:
            if current_time >= task.next_execution or task.execute_immediately:
                if task.task_type == ACCOUNT_CREATION:
                    email = task.task_data["email"]
                    password = task.task_data["password"]
                    protocol = task.task_data["protocol"]
                    server = task.task_data["server"]
                    port = task.task_data["port"]
                    update_interval = task.task_data["interval"]
                    selected_inboxes = task.task_data["selected_inboxes"]
                    account_id = email_service.create_account(
                        email,
                        password,
                        protocol,
                        server,
                        port,
                        update_interval,
                        selected_inboxes,
                    )
                    if account_id:
                        logging.info(
                            f"Account created successfully for {email}. Adding to email retrieval queue."
                        )
                        task_queue.put(
                            Task.create_task(
                                EMAIL_RETRIEVAL,
                                {"account_id": account_id},
                                interval=update_interval,
                                execute_immediately=True,
                            )
                        )
                    else:
                        logging.error(f"Failed to create account for {email}.")

                elif task.task_type == EMAIL_RETRIEVAL:
                    account_id = task.task_data["account_id"]
                    db = next(get_db())  # Get a database session
                    account = db.query(Account).filter(Account.id == account_id).first()
                    if account:
                        email_service.fetch_and_archive_emails(
                            account_id,
                            account.protocol,
                            account.server,
                            account.port,
                            account.email,
                            account.password,
                            account.selected_inboxes,
                        )
                        logging.info(
                            f"Email retrieval completed for account {account_id}."
                        )
                    else:
                        logging.error(f"Account with ID {account_id} not found.")

                # Update the next execution time based on the interval (if provided)
                if task.interval is not None:
                    task.next_execution = current_time + task.interval
                    task.execute_immediately = (
                        False  # Set execute_immediately back to False
                    )
                    task_queue.put(task.to_dict())
            else:
                # If the task is not ready for execution, put it back in the queue
                task_queue.put(task.to_dict())
                time.sleep(1)
        else:
            # If no tasks are available, sleep for a short interval before checking again
            time.sleep(1)


# Start worker thread
task_worker = threading.Thread(target=process_tasks)

# Initialize email retrieval tasks
initialize_email_retrieval_tasks()

task_worker.start()

from fastapi import APIRouter
from models import AccountData
import email_archiver as email_archiver
import imaplib
import poplib
import sqlite3
from queue_manager import task_queue, ACCOUNT_CREATION, Task
import queue

router = APIRouter()

@router.post("/get_available_inboxes")
def get_available_inboxes(account_data: AccountData):
    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port

    if not all([email, password, protocol.lower(), server, port]):
        return {"error": "Missing required fields"}

    try:
        available_inboxes = email_archiver.get_available_inboxes(email, password, protocol, server, port)
        
        # Clean available inboxes for empty strings
        available_inboxes = [inbox for inbox in available_inboxes if inbox]

        return {"available_inboxes": available_inboxes}
    except (imaplib.IMAP4.error, poplib.error_proto) as e:
        error_message = f"Failed to connect to the {protocol.upper()} server. Please check the server details."
        return {"error": error_message}
    
@router.post("/create_account")
def create_account(account_data: AccountData):
    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port
    interval = account_data.interval
    selected_inboxes = account_data.selected_inboxes

    if not all([email, password, protocol.lower(), server, port]):
        return {"error": "Missing required fields"}

    task_data = {
        "email": email,
        "password": password,
        "protocol": protocol,
        "server": server,
        "port": port,
        "selected_inboxes": selected_inboxes,
        "interval": interval,
    }
    task = Task.create_task(ACCOUNT_CREATION, task_data)
    task_queue.put(task)

    return {"message": "Account creation queued successfully"}
    
@router.get("/get_accounts")
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
            "available_inboxes": account[7].split(",") if account[7] else [],
            "selected_inboxes": account[8].split(",") if account[8] else [],
            "interval": account[9],
        }
        for account in accounts
    ]
    return accounts_data


@router.post("/update_account/{account_id}")
def update_account(account_id: int, account_data: AccountData):
    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port
    selected_inboxes = account_data.selected_inboxes

    conn = sqlite3.connect("data/email_archive.db")
    cursor = conn.cursor()

    cursor.execute("SELECT available_inboxes FROM accounts WHERE id = ?", (account_id,))
    available_inboxes = cursor.fetchone()[0]

    email_archiver.update_account(
        conn, account_id, email, password, protocol.lower(), server, port, available_inboxes, selected_inboxes
    )
    conn.close()

    return {"message": "Account updated successfully"}

@router.delete("/delete_account/{account_id}", status_code=200)
def delete_account(account_id: int):
    conn = sqlite3.connect("data/email_archive.db")
    email_archiver.delete_account(conn, account_id)
    conn.close()
    return {"message": "Account deleted successfully"}

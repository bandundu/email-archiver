import logging

from fastapi import APIRouter
from api.schemas.schemas import AccountData

# Import services
import services.email_service as email_service
import services.queue_service as queue_service


router = APIRouter()


@router.post("/get_available_inboxes")
def get_available_inboxes_route(account_data: AccountData):
    
    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port

    if not all([email, password, protocol.lower(), server, port]):
        logging.error("Missing required fields")
        return {"error": "Missing required fields"}

    try:
        available_inboxes = email_service.get_available_inboxes(
            email, password, protocol, server, port
        )
    except Exception as e:
        logging.error(f"Failed to get available inboxes: {e}")
        return {"error": "Failed to get available inboxes"}

    logging.debug(f"Available inboxes: {available_inboxes}")
    return {"available_inboxes": available_inboxes}


@router.post("/create_account")
def create_account_route(account_data: AccountData):

    logging.debug(f"Received request to create account for {account_data.email}")

    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port
    interval = account_data.interval
    selected_inboxes = account_data.selected_inboxes

    if not all([email, password, protocol.lower(), server, port]):
        logging.error("Missing required fields")
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

    logging.debug(f"Queueing account creation for {email}")
    task = queue_service.Task.create_task(queue_service.ACCOUNT_CREATION, task_data)
    queue_service.task_queue.put(task)

    return {"message": "Account creation queued successfully"}


@router.get("/get_accounts")
def get_accounts_route():
    logging.debug("Received request to get accounts")
    logging.info(f"Received request at example endpoint: {request.method} {request.url}")
    logging.info(f"Request headers: {request.headers}")
    accounts = email_service.read_accounts()

    accounts_data = [
        {
            "id": account.id,
            "email": account.email,
            "protocol": account.protocol,
            "server": account.server,
            "port": account.port,
            "available_inboxes": (
                account.available_inboxes.split(",")
                if account.available_inboxes
                else []
            ),
            "selected_inboxes": (
                account.selected_inboxes.split(",") if account.selected_inboxes else []
            ),
            "interval": account.update_interval,
        }
        for account in accounts
    ]

    return accounts_data


@router.post("/update_account/{account_id}")
def update_account_route(account_id: int, account_data: AccountData):

    logging.debug(f"Received request to update account {account_id}")

    email = account_data.email
    password = account_data.password
    protocol = account_data.protocol
    server = account_data.server
    port = account_data.port
    selected_inboxes = account_data.selected_inboxes

    available_inboxes = email_service.get_available_inboxes_from_db(account_id)
    logging.debug(f"Available inboxes: {available_inboxes}")

    email_service.update_account(
        account_id,
        email,
        password,
        protocol.lower(),
        server,
        port,
        available_inboxes,
        selected_inboxes,
    )

    logging.debug(f"Account updated successfully")

    return {"message": "Account updated successfully"}


@router.delete("/delete_account/{account_id}", status_code=200)
def delete_account_route(account_id: int):
    email_service.delete_account(account_id)
    logging.debug(f"Account {account_id} deleted successfully")
    return {"message": "Account deleted successfully"}

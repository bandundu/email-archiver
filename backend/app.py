# Setting up logging
import logging
from config.logging_config import configure_logging
from config.config import config

configure_logging(config.LOG_LEVEL)

# Load the encryption cipher suite
from utils.encryption import cipher_suite

# Initialize the database
from models.database import initialize_database

initialize_database()

# Import FastAPI and the CORS middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# Import routers for different API endpoints
from api.routes.accounts import router as accounts_router
from api.routes.attachments import router as attachments_router
from api.routes.emails import router as emails_router
from api.routes.exports import router as exports_router
from api.routes.utilities import router as utilities_router

# Initialize the FastAPI application
app = FastAPI()

# Include routers for different API endpoints
app.include_router(accounts_router, prefix="/accounts")
app.include_router(attachments_router, prefix="/attachments")
app.include_router(emails_router, prefix="/emails")
app.include_router(exports_router, prefix="/exports")
app.include_router(utilities_router, prefix="/utilities")


# Set up CORS middleware to allow requests from any origin

# Literal quote from the help page: "Also, allow_origins cannot be set to [*] for credentials to be allowed, origins must be specified."  !!

# As others have said REMOVE allow_methods=["*"], if the origin is a wildcard otherwise it WILL NOT WORK
app.add_middleware(
    CORSMiddleware,
    allow_origins= ['http://localhost:3000', 'http://127.0.0.1:3000', "http://192.168.0.112:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":

    uvicorn.run(app, host="localhost", port=5050)

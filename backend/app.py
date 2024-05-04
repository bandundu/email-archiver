from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import email_archiver as email_archiver
from email_archiver import initialize_database
from encryption import cipher_suite

# Import routers
from api.accounts import router as accounts_router
from api.attachments import router as attachments_router
from api.emails import router as emails_router
from api.exports import router as exports_router
from api.utilities import router as utilities_router

app = FastAPI()

# Include routers for different API endpoints
app.include_router(accounts_router, prefix="/accounts")
app.include_router(attachments_router, prefix="/attachments")
app.include_router(emails_router, prefix="/emails")
app.include_router(exports_router, prefix="/exports")
app.include_router(utilities_router, prefix="/utilities")


# Set up CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":

    # Create the 'data' directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        # Initialize the database
        initialize_database()
    except InvalidToken:
        print("Error: The provided Fernet key is incompatible with the existing database.")
        exit(1)

    # Start the FastAPI application using Uvicorn
    import uvicorn
    uvicorn.run(app, host="localhost", port=5050)
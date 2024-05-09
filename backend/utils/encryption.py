# Utilities are used for more low-level operations needed by services or application initialization.

import os
import re
from cryptography.fernet import Fernet
import logging
from config.config import config


def generate_or_load_fernet_key():
    """
    Generate a new Fernet key if SECRET_KEY is not set in the environment variable,
    otherwise use the existing SECRET_KEY value.
    """
    secret_key = config.SECRET_KEY
    if secret_key:
        # If SECRET_KEY is present and not empty, use it as the Fernet key
        fernet_key = secret_key
        logging.info(f"Using preset Fernet key: {fernet_key}")
    else:
        # If SECRET_KEY is empty or not present, generate a new Fernet key
        fernet_key = Fernet.generate_key().decode()
        logging.info(f"Generated new Fernet key: {fernet_key}")

    # Read the contents of the .env file
    if os.path.exists(".env"):
        logging.debug("Reading .env file")
        with open(".env", "r") as f:
            env_contents = f.read().strip() # Strip whitespace

        # Check if the file is empty or the first line is empty
        if not env_contents or env_contents.startswith("\n"):
            # Write the new SECRET_KEY on the first line
            updated_contents = f"SECRET_KEY={fernet_key}\n{env_contents.lstrip()}"
            logging.debug("Updated .env file with new SECRET_KEY")
        else:
            logging.debug("Checking for existing SECRET_KEY in .env file")
            # Check if SECRET_KEY exists in the .env file
            if "SECRET_KEY=" in env_contents:
                # Update the existing SECRET_KEY with the generated Fernet key
                updated_contents = re.sub(
                    r"SECRET_KEY=.*", f"SECRET_KEY={fernet_key}", env_contents
                )
                logging.debug("Updated existing SECRET_KEY in .env file")
            else:
                # Append the new SECRET_KEY to the .env file
                updated_contents = env_contents + f"\nSECRET_KEY={fernet_key}"
                logging.debug("Appended new SECRET_KEY to .env file")
    else:
        # If the file doesn't exist, create it with the new SECRET_KEY
        updated_contents = f"SECRET_KEY={fernet_key}\n"
        logging.debug("Created new .env file with SECRET")

    # Write the updated contents back to the .env file
    with open(".env", "w") as f:
        f.write(updated_contents)
    logging.debug("Wrote updated contents to .env file")

    return fernet_key

# Load the secret key from the environment variable
try:
    fernet_key = generate_or_load_fernet_key().encode()
    cipher_suite = Fernet(fernet_key)
except ValueError as e:
    logging.error("Invalid Fernet key.")
    logging.error("Please ensure that the SECRET_KEY in the .env file is a valid 32 url-safe base64-encoded bytes.")
    logging.error("If the issue persists, try deleting the SECRET_KEY from the .env file and restarting the application.")
    cipher_suite = None
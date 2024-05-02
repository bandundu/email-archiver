import os
import re
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

def generate_or_load_fernet_key():
    """
    Generate a new Fernet key if SECRET_KEY is not set in the environment variable,
    otherwise use the existing SECRET_KEY value.
    """
    secret_key = os.getenv("SECRET_KEY")

    if secret_key:
        # If SECRET_KEY is present and not empty, use it as the Fernet key
        fernet_key = secret_key
        print(f"Using preset Fernet key: {fernet_key}")
    else:
        # If SECRET_KEY is empty or not present, generate a new Fernet key
        fernet_key = Fernet.generate_key().decode()
        print(f"Generated new Fernet key: {fernet_key}")

        # Read the contents of the .env file
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                env_contents = f.read().strip()  # Strip whitespace

            # Check if the file is empty or the first line is empty
            if not env_contents or env_contents.startswith("\n"):
                # Write the new SECRET_KEY on the first line
                updated_contents = f"SECRET_KEY={fernet_key}\n{env_contents.lstrip()}"
            else:
                # Check if SECRET_KEY exists in the .env file
                if "SECRET_KEY=" in env_contents:
                    # Update the existing SECRET_KEY with the generated Fernet key
                    updated_contents = re.sub(
                        r"SECRET_KEY=.*", f"SECRET_KEY={fernet_key}", env_contents
                    )
                else:
                    # Append the new SECRET_KEY to the .env file
                    updated_contents = env_contents + f"\nSECRET_KEY={fernet_key}"

        else:
            # If the file doesn't exist, create it with the new SECRET_KEY
            updated_contents = f"SECRET_KEY={fernet_key}\n"

        # Write the updated contents back to the .env file
        with open(".env", "w") as f:
            f.write(updated_contents)

    return fernet_key

# Load the secret key from the environment variable
fernet_key = generate_or_load_fernet_key().encode()
cipher_suite = Fernet(fernet_key)
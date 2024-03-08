from cryptography.fernet import Fernet

# Generate a secret key for encryption
secret_key = Fernet.generate_key()

# Save the secret key to the configuration file
with open('secret.key', 'wb') as key_file:
    key_file.write(secret_key)
# Briefbox

Briefbox is a simple tool for archiving emails from multiple IMAP and POP3 accounts. It provides a user-friendly web interface for managing email accounts, searching archived emails, and viewing email details along with attachments.

## Features

- Add, update, and delete IMAP and POP3 email accounts
- Automatically fetch and archive emails from configured accounts
- Search archived emails based on subject, sender, recipients, or body content
- View email details, including subject, sender, recipients, date, and body
- Download email attachments
- Periodic email archiving to keep the database up to date

## Prerequisites

- Docker
- Docker Compose

## Setup and Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/email-archiver.git
   cd email-archiver
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

3. Access the web interface by opening a web browser and navigating to `http://localhost:5000`.

4. Use the web interface to add email accounts, search for emails, and view email details.

## Configuration

The project uses a SQLite database to store the archived emails and account information. The database file is located at `email_archive.db` in the project directory.

To configure the email archiving settings, you can modify the following files:

- `config.py`: Contains the configuration for generating the secret key used for encryption.
- `email_archiver.py`: Contains the main logic for fetching and archiving emails from the configured accounts.

## Project Structure

```
.
├── Dockerfile
├── README.md
├── __pycache__
│   ├── email_archiver.cpython-310.pyc
│   └── email_archiver.cpython-39.pyc
├── app.py
├── config.py
├── docker-compose.yml
├── email_archive.db
├── email_archiver.py
├── requirements.txt
├── secret.key
└── templates
    ├── base.html
    ├── create_account.html
    ├── delete_account.html
    ├── email_details.html
    ├── index.html
    ├── list_accounts.html
    ├── search_emails.html
    └── update_account.html
```

- `Dockerfile`: Defines the Docker image for the Briefbox application.
- `app.py`: The main Flask application file that handles the web routes and interfaces with the email archiver.
- `config.py`: Contains the configuration for generating the secret key used for encryption.
- `docker-compose.yml`: Defines the Docker Compose configuration for running the Briefbox application.
- `email_archive.db`: The SQLite database file that stores the archived emails and account information.
- `email_archiver.py`: Contains the main logic for fetching and archiving emails from the configured accounts.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `secret.key`: Stores the secret key used for encryption.
- `templates/`: Contains the HTML templates for the web interface.

## Future Enhancements

- Support for additional email protocols
- Advanced search capabilities (e.g., date range, multiple criteria)
- Email export functionality
- Improved user interface and user experience

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request. Make sure to follow the project's code of conduct.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contact

For any questions or inquiries, please contact me at charlesdavid@mupende.com

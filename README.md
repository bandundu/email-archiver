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
   git clone https://github.com/bandundu/email-archiver.git
   cd email-archiver
   ```

2. Generate the Fernet key and populate the `.env` file:
   ```bash
   make generate-key
   ```

3. Build the Docker containers:
   ```bash
   make build
   ```

4. Run the Docker containers:
   ```bash
   make run
   ```

5. Access the web interface by opening a web browser and navigating to `http://localhost:5000`.

6. Use the web interface to add email accounts, search for emails, and view email details.

## Configuration

The project uses a SQLite database to store the archived emails and account information. The database file is located at `email_archive.db` in the project directory.

To configure the email archiving settings, you can modify the `email_archiver.py` file, which contains the main logic for fetching and archiving emails from the configured accounts.

## Reusing an Existing Database

If you want to reuse an existing database with a previously generated Fernet key, follow these steps:

1. Copy your existing `email_archive.db` file into the project directory.

2. Copy the `SECRET_KEY` value from your existing `.env` file.

3. Run `make generate-key` to generate a new `.env` file.

4. Replace the `SECRET_KEY` value in the newly generated `.env` file with the value you copied from your existing `.env` file.

5. Run `make build` and `make run` to start the project with your existing database.

## Project Structure

```
.
├── Dockerfile
├── Makefile
├── README.md
├── app.py
├── docker-compose.yml
├── email_archive.db
├── email_archiver.py
├── requirements.txt
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
- `Makefile`: Contains commands for generating the Fernet key, building and running the Docker containers, and cleaning up.
- `app.py`: The main Flask application file that handles the web routes and interfaces with the email archiver.
- `docker-compose.yml`: Defines the Docker Compose configuration for running the Briefbox application.
- `email_archive.db`: The SQLite database file that stores the archived emails and account information.
- `email_archiver.py`: Contains the main logic for fetching and archiving emails from the configured accounts.
- `requirements.txt`: Lists the Python dependencies required for the project.
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

For any questions or inquiries, please contact me at charlesdavid@mupende.com.
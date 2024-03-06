# Email Archiver

Super simple email archiver with a command-line interface that allows you to archive emails from multiple IMAP accounts into a SQLite database. It provides functionality to manage IMAP accounts, search for emails, and retrieve email details along with attachments.

## Features

- Create, list, update, and delete IMAP accounts
- Fetch and archive emails from multiple IMAP accounts
- Search for emails based on subject, sender, recipients, or body
- Retrieve email details and attachments
- Periodically run the email archiving process

## Usage

To use the Email Archiver, run the following commands:

- Create a new IMAP account:

  ```bash
  python email_archiver.py create_account username password imap_server imap_port mailbox
  ```

- List all IMAP accounts:

  ```bash
  python email_archiver.py list_accounts
  ```

- Update an IMAP account:

  ```bash
  python email_archiver.py update_account account_id username password imap_server imap_port mailbox
  ```

- Delete an IMAP account:

  ```bash
  python email_archiver.py delete_account account_id
  ```

- Search for emails:

  ```bash
  python email_archiver.py search_emails query
  ```

- Get email details:

  ```bash
  python email_archiver.py get_email email_id
  ```

- Run the email archiver:

  ```bash
  python email_archiver.py run_archiver
  ```

## Future Enhancements

The following features are planned for future implementation:

- Web-based frontend for managing IMAP accounts and browsing archived emails
- Support for additional email protocols (e.g., POP3)
- Integration with external storage services for storing attachments
- Advanced search capabilities (e.g., date range, multiple criteria)
- Email export functionality

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## Contact

For any questions or feature requests, please contact me at charlesdavid@mupende.com.

## License

This project is licensed under the [MIT License](LICENSE).

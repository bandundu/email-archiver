🚨🚨🚨 IMPORTANT DISCLAIMER 🚨🚨🚨

**This project is currently still in early development and lacks proper authentication.** It is **NOT** recommended to expose this application to the public as you will be providing the world your emails. Use at your own discretion and only in a controlled environment for now.

# Briefbox

Briefbox is a powerful tool for archiving emails from multiple IMAP and POP3 accounts. It provides a user-friendly web interface for managing email accounts, searching archived emails, and viewing email details along with attachments. One of the standout features of Briefbox is its advanced search functionality, which allows users to quickly find specific emails using various criteria.

![grafik](https://github.com/bandundu/email-archiver/assets/41874924/6b0b06f3-0f49-4f55-82a9-3471c7ee0c42)
![grafik](https://github.com/bandundu/email-archiver/assets/41874924/856f4f56-6016-476b-857f-f63fe37706aa)


## Features

- Add, update, and delete IMAP and POP3 email accounts
- Automatically fetch and archive emails from configured accounts
- **Powerful search functionality:**
  - Search archived emails based on subject, sender, recipients, or body content
  - Perform case-insensitive searches for more accurate results
  - Search for emails by date using flexible date formats (e.g., "26 Jan 2024", "2024-01-26", "January 26, 2024")
  - **Search for emails within a specific date range using the format "DD MMM YYYY - DD MMM YYYY" (e.g., "26 Jan 2024 - 28 Jan 2024")**
  - Use multiple search terms to narrow down results
  - Examples:
    - Search for emails from a specific sender: `john@example.com`
    - Find emails with a specific subject: `"Project Update"`
    - Search for emails containing certain keywords in the body: `meeting agenda`
    - Combine multiple criteria: `from:john@example.com subject:"Project Update" meeting`
    - Search for emails by date: `26 Jan 2024`, `2024-01-26`, `January 26, 2024`
    - **Search for emails within a date range: `26 Jan 2024 - 28 Jan 2024`**
- View email details, including subject, sender, recipients, date, and body
- Download email attachments
- Periodic email archiving to keep the database up to date

## Prerequisites

- Docker
- Docker Compose

Here's the updated Setup and Usage section for your README:

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

3. Pull the pre-built Docker image from Docker Hub:

```bash
docker-compose pull
```

4. Run the Docker containers:

```bash
docker-compose up
```

5. Access the web interface by opening a web browser and navigating to `http://localhost:3000`.

6. Use the web interface to add email accounts, search for emails, and view email details.

## Future Enhancements

- Email export functionality
- Gmail and Outlook OAuth2 authentication
- Advanced search capabilities (e.g., date range, multiple criteria)
- Improved user interface and user experience

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request. Make sure to follow the project's code of conduct.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

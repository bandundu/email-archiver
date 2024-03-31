🚨🚨🚨 IMPORTANT DISCLAIMER 🚨🚨🚨

**This project is currently in early development, and things may break unexpectedly. It also lacks proper authentication.** It is **NOT** recommended to expose this application to the internet, as you will be providing the world access to your emails. Use at your own discretion and only in a controlled environment for now.

While feedback and contributions are appreciated during this early development phase, please note that this project is not yet suitable for use as a stable email backup solution. The first stable release is targeted for the end of the year. If you require a reliable email archiving solution, it is advisable to wait until the stable release.

**Use at your own risk and in a controlled environment only.**

# Briefbox

Briefbox is a tool for archiving emails from multiple IMAP and POP3 accounts. It provides a user-friendly web interface for managing email accounts, searching archived emails, and viewing email details along with attachments. One of the standout features of Briefbox is its advanced search functionality, which allows users to quickly find specific emails using various criteria.

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

## Setup and Usage

1. Create a `docker-compose.yml` file in a folder of your chosing with the following content:

```yaml
version: '3'

services:
  backend:
    # latest-arm for ARM devices like Raspberry Pi
    image: bandundu/briefbox-backend:latest
    ports:
      - "5000:5000"
    volumes:
      - ./:/app/data
    environment:
      - FLASK_ENV=development
      - FLASK_APP=app.py

  frontend:
    # latest-arm for ARM devices like Raspberry Pi
    image: bandundu/briefbox-frontend:latest
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

> **Note:** For ARM devices like Raspberry Pi, use the `latest-arm` tag for both backend and frontend images.

2. Run the following command to start the containers:

```bash
docker-compose up
```

3. Access the web interface by opening a web browser and navigating to `http://localhost:3000`.

4. Use the web interface to add email accounts, search for emails, and view email details.

Here's the bare-metal installation section in the requested format:

## Bare-Metal Installation

If you prefer to run Briefbox without using Docker, you can follow these steps to set up the backend and frontend separately.

### Prerequisites

- Python 3.9
- Node.js and npm

### Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/bandundu/email-archiver.git
```

2. Navigate to the backend directory:

```bash
cd email-archiver/backend
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate the virtual environment:

```bash
source venv/bin/activate
```

5. Install the required dependencies:

```bash
pip install -r requirements.txt
```

6. Run the backend server:

```bash
python app.py
```

The backend server will start running on `http://localhost:5000`.

### Frontend Setup

1. In a separate terminal, navigate to the frontend directory:

```bash
cd email-archiver/frontend/briefbox-front
```

2. Install the required dependencies:

```bash
npm install
```

3. Start the frontend development server:

```bash
npm run start
```

The frontend server will start running on `http://localhost:3000`.

4. Access the web interface by opening a web browser and navigating to `http://localhost:3000`.

### Usage

With both the backend and frontend servers running, you can use the web interface to add email accounts, search for emails, and view email details.

Note: Make sure to keep both the backend and frontend servers running simultaneously for the application to function properly.

## Future Enhancements

- Email export functionality
- Gmail and Outlook OAuth2 authentication
- Advanced search capabilities (e.g., date range, multiple criteria)
- Improved user interface and user experience

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request. Make sure to follow the project's code of conduct.

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import email_archiver
import sqlite3
from dateutil import parser
import threading
from dotenv import load_dotenv
from email_archiver import initialize_database
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
#CORS(app)  # Enable CORS for all routes and origins
cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)

@app.template_filter('format_date')
def format_date(date_str):
    # Use dateutil.parser to handle various date formats with or without timezone information
    date_obj = parser.parse(date_str)
    # Format the date as desired (e.g., without timezone information)
    return date_obj.strftime('%a, %d %b %Y %H:%M:%S')

app.jinja_env.filters['format_date'] = format_date

@app.route('/')
def index():
    conn = sqlite3.connect('email_archive.db')
    cursor = conn.cursor()

    # Fetch the latest archived emails
    cursor.execute("SELECT * FROM emails ORDER BY date DESC LIMIT 10")
    latest_emails = cursor.fetchall()

    # Fetch summary statistics
    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM accounts")
    total_accounts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attachments")
    total_attachments = cursor.fetchone()[0]

    conn.close()

    return render_template('index.html', latest_emails=latest_emails, total_emails=total_emails,
                           total_accounts=total_accounts, total_attachments=total_attachments)


@app.route('/stats')
def get_stats():
    conn = sqlite3.connect('email_archive.db')
    cursor = conn.cursor()

    # Fetch summary statistics
    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM accounts")
    total_accounts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attachments")
    total_attachments = cursor.fetchone()[0]

    conn.close()

    stats = {
        'totalEmails': total_emails,
        'totalAccounts': total_accounts,
        'totalAttachments': total_attachments
    }

    # create response and set CORS headers
    response = jsonify(stats)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/latest-emails')
def latest_emails():
    conn = sqlite3.connect('email_archive.db')
    cursor = conn.cursor()

    # Fetch the latest archived emails
    cursor.execute("SELECT subject, sender, date FROM emails ORDER BY date DESC LIMIT 5")
    latest_emails = cursor.fetchall()

    conn.close()

    # Format the latest emails as a list of dictionaries
    emails_data = [
        {
            'subject': email[0],
            'sender': email[1],
            'date': format_date(email[2])
        }
        for email in latest_emails
    ]

    # create response and set CORS headers
    response = jsonify(emails_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Check if the request content type is JSON
        if request.is_json:
            # Parse data as JSON
            data = request.get_json()
        else:
            # Otherwise, treat it as form data
            data = request.form

        email = data.get('email')
        password = data.get('password')
        protocol = data.get('protocol')
        server = data.get('server')
        port = data.get('port')

        # Validate the extracted data
        if not all([email, password, protocol.lower(), server, port]):
            # Respond with an error if any field is missing or the request is JSON
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            else:
                return render_template('create_account.html', error_message='Missing required fields')

        conn = sqlite3.connect('email_archive.db')
        try:
            # Assume email_archiver.create_account function exists and handles the DB operations
            email_archiver.create_account(conn, email, password, protocol, server, port)
            conn.close()
            if request.is_json:
                # For JSON requests, return a success response in JSON
                return jsonify({'message': 'Account created successfully'}), 200
            else:
                # For form data requests, redirect as before
                return redirect(url_for('list_accounts'))
        except sqlite3.IntegrityError:
            conn.close()
            error_message = f"An account with email '{email}' already exists. Please use a different email."
            if request.is_json:
                return jsonify({'error': error_message}), 400
            else:
                return render_template('create_account.html', error_message=error_message)

    # For GET requests or other non-POST methods
    return render_template('create_account.html')

@app.route('/emails')
def get_emails():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    sort_by = request.args.get('sort_by', default='date')
    sort_order = request.args.get('sort_order', default='desc')

    conn = sqlite3.connect('email_archive.db')
    cursor = conn.cursor()

    # Get the total count of emails
    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]

    # Calculate the offset based on the page and per_page values
    offset = (page - 1) * per_page

    # Fetch the emails with pagination
    query = f"SELECT * FROM emails ORDER BY {sort_by} {sort_order} LIMIT {per_page} OFFSET {offset}"
    cursor.execute(query)
    emails = cursor.fetchall()

    conn.close()

    email_data = [
        {
            'id': email[0],
            'account_id': email[1],
            'subject': email[2],
            'sender': email[3],
            'recipients': email[4],
            'date': email[5],
            'body': email[6],
            'unique_id': email[7]
        }
        for email in emails
    ]

    response = make_response(jsonify({'emails': email_data, 'total_emails': total_emails}))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/list_accounts')
def list_accounts():
    conn = sqlite3.connect('email_archive.db')
    accounts = email_archiver.read_accounts(conn)
    conn.close()
    return render_template('list_accounts.html', accounts=accounts)

@app.route('/get_accounts', methods=['GET'])
def get_accounts():
    conn = sqlite3.connect('email_archive.db')
    accounts = email_archiver.read_accounts(conn)
    conn.close()

    accounts_data = [
        {
            'id': account[0],
            'email': account[1],
            'protocol': account[3],
            'server': account[4],
            'port': account[5]
        }
        for account in accounts
    ]
    # create response and set CORS headers
    response = jsonify(accounts_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/update_account/<int:account_id>', methods=['GET', 'POST'])
def update_account(account_id):
    conn = sqlite3.connect('email_archive.db')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        protocol = request.form['protocol']
        server = request.form['server']
        port = int(request.form['port'])
        mailbox = request.form['mailbox']
        email_archiver.update_account(conn, account_id, email, password, protocol.lower(), server, port, mailbox)
        conn.close()
        return redirect(url_for('list_accounts'))
    account = email_archiver.get_account(conn, account_id)
    conn.close()
    return render_template('update_account.html', account=account)

@app.route('/delete_account/<int:account_id>', methods=['GET', 'POST'])
def delete_account(account_id):
    conn = sqlite3.connect('email_archive.db')
    if request.method == 'POST':
        email_archiver.delete_account(conn, account_id)
        conn.close()
        return redirect(url_for('list_accounts'))
    account = email_archiver.get_account(conn, account_id)
    conn.close()
    return render_template('delete_account.html', account=account)

@app.route('/delete_email/<int:email_id>', methods=['DELETE'])
def delete_email(email_id):
    conn = sqlite3.connect('email_archive.db')
    cursor = conn.cursor()

    try:
        # Delete the email from the emails table
        cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))

        # Delete the associated attachments from the attachments table
        cursor.execute("DELETE FROM attachments WHERE email_id = ?", (email_id,))

        conn.commit()
        conn.close()

        # create response and set CORS headers
        response = jsonify({'message': 'Email deleted successfully'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        conn.rollback()
        conn.close()
        # create response and set CORS headers
        response = jsonify({'error': 'An error occurred while deleting the email'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
@app.route('/search_emails', methods=['GET', 'POST'])
def search_emails():
    if request.method == 'POST':
        query = request.form['query']
        conn = sqlite3.connect('email_archive.db')
        emails = email_archiver.search_emails(conn, query)
        conn.close()
        return render_template('search_emails.html', emails=emails, query=query)
    return render_template('search_emails.html')

# @app.route('/email_details/<int:email_id>')
# def email_details(email_id):
#     conn = sqlite3.connect('email_archive.db')
#     email, attachments, attachment_filenames = email_archiver.get_email_details(conn, email_id)
#     conn.close()
#     return render_template('email_details.html', email=email, attachments=attachments, attachment_filenames=attachment_filenames)

@app.route('/email_details/<int:email_id>')
def email_details(email_id):
    conn = sqlite3.connect('email_archive.db')
    email, attachments, attachment_filenames = email_archiver.get_email_details(conn, email_id)
    conn.close()

    if email:
        email_data = {
            'id': email[0],
            'account_id': email[1],
            'subject': email[2],
            'sender': email[3],
            'recipients': email[4],
            'date': email[5],
            'body': email[6],
            'content_type': email[7]
        }
        attachment_data = [
            {
                'id': attachment[0],
                'filename': attachment[1]
            }
            for attachment in attachments
        ]
        # create response and set CORS headers
        response = jsonify({'email': email_data, 'attachments': attachment_data})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        # create response and set CORS headers
        response = jsonify({'error': 'Email not found'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/download_attachment/<int:attachment_id>')
def download_attachment(attachment_id):
    conn = sqlite3.connect('email_archive.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename, content FROM attachments WHERE id = ?", (attachment_id,))
    attachment = cursor.fetchone()
    conn.close()
    
    if attachment:
        filename, content = attachment
        response = make_response(content)
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
        # add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        # create response and set CORS headers
        response = jsonify({'error': 'Attachment not found'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
@app.route('/export_email/<int:email_id>')
def export_email(email_id):
    conn = sqlite3.connect('email_archive.db')
    email_data = email_archiver.export_email(conn, email_id)
    conn.close()
    
    if email_data:
        response = make_response(email_data)
        response.headers.set('Content-Type', 'message/rfc822')
        response.headers.set('Content-Disposition', 'attachment', filename=f"email_{email_id}.eml")
        # add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        # create response and set CORS headers
        response = jsonify({'error': 'Email not found'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/export_all_emails')
def export_all_emails():
    conn = sqlite3.connect('email_archive.db')
    zip_data = email_archiver.export_all_emails(conn)
    conn.close()
    
    response = make_response(zip_data)
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set('Content-Disposition', 'attachment', filename="all_emails.zip")
    # add CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/export_search_results', methods=['POST'])
def export_search_results():
    query = request.form['query']
    conn = sqlite3.connect('email_archive.db')
    zip_data = email_archiver.export_search_results(conn, query)
    conn.close()
    
    response = make_response(zip_data)
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set('Content-Disposition', 'attachment', filename="search_results.zip")
    # add CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def run_archiver_thread():
    email_archiver.run_archiver()

if __name__ == '__main__':
    # Initialize the database
    initialize_database()
    # Start the email archiving thread
    archiver_thread = threading.Thread(target=run_archiver_thread)
    archiver_thread.daemon = True
    archiver_thread.start()
    
    # Run the Flask app
    app.run(host='127.0.0.1', port=5000, debug=True)
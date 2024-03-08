from flask import Flask, render_template, request, redirect, url_for, make_response
import email_archiver
import sqlite3
from dateutil import parser
import threading

app = Flask(__name__)


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
    cursor.execute("SELECT * FROM emails ORDER BY date DESC LIMIT 5")
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

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        protocol = request.form['protocol']
        server = request.form['server']
        port = request.form['port']
        conn = sqlite3.connect('email_archive.db')
        try:
            email_archiver.create_account(conn, email, password, protocol, server, port)
            conn.close()
            return redirect(url_for('list_accounts'))
        except sqlite3.IntegrityError:
            conn.close()
            error_message = f"An account with email '{email}' already exists. Please use a different email."
            return render_template('create_account.html', error_message=error_message)
    return render_template('create_account.html')

@app.route('/list_accounts')
def list_accounts():
    conn = sqlite3.connect('email_archive.db')
    accounts = email_archiver.read_accounts(conn)
    conn.close()
    return render_template('list_accounts.html', accounts=accounts)

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
        email_archiver.update_account(conn, account_id, email, password, protocol, server, port, mailbox)
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

@app.route('/search_emails', methods=['GET', 'POST'])
def search_emails():
    if request.method == 'POST':
        query = request.form['query']
        conn = sqlite3.connect('email_archive.db')
        emails = email_archiver.search_emails(conn, query)
        conn.close()
        return render_template('search_emails.html', emails=emails, query=query)
    return render_template('search_emails.html')

@app.route('/email_details/<int:email_id>')
def email_details(email_id):
    conn = sqlite3.connect('email_archive.db')
    email, attachments, attachment_filenames = email_archiver.get_email_details(conn, email_id)
    conn.close()
    return render_template('email_details.html', email=email, attachments=attachments, attachment_filenames=attachment_filenames)

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
        return response
    else:
        return "Attachment not found", 404

def run_archiver_thread():
    email_archiver.run_archiver()

if __name__ == '__main__':
    # Start the email archiving thread
    archiver_thread = threading.Thread(target=run_archiver_thread)
    archiver_thread.daemon = True
    archiver_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
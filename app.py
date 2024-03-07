from flask import Flask, render_template, request, redirect, url_for
import email_archiver
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        protocol = request.form['protocol']
        conn = sqlite3.connect('email_archive.db')
        email_archiver.create_account(conn, email, password, protocol)
        conn.close()
        return redirect(url_for('list_accounts'))
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
    email, attachments = email_archiver.get_email_details(conn, email_id)
    conn.close()
    return render_template('email_details.html', email=email, attachments=attachments)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
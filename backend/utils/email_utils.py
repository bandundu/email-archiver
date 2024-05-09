# Utilities are used for more low-level operations needed by services or application initialization.

import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime


def parse_date(date_str):
    if date_str is None:
        return None

    try:
        date_tuple = parsedate_to_datetime(date_str)
        return date_tuple
    except (TypeError, ValueError):
        return None


def decode_header(header):
    if header is None:
        return ""
    parts = email.header.decode_header(header)
    decoded_parts = [
        part.decode(encoding or "utf-8") if isinstance(part, bytes) else part
        for part, encoding in parts
    ]
    return "".join(decoded_parts)


def extract_body(email_message):
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                body_part = payload.decode(charset or "utf-8", errors="replace")
                body_part = body_part.replace(
                    "\r\n", "<br>"
                )  # Replace escaped newlines with <br> tags
                body += body_part
    else:
        payload = email_message.get_payload(decode=True)
        charset = email_message.get_content_charset()
        body = payload.decode(charset or "utf-8", errors="replace")
        body = body.replace("\r\n", "<br>")  # Replace escaped newlines with <br> tags

    return body


def decode_filename(filename):
    if filename is None:
        return ""
    parts = email.header.decode_header(filename)
    decoded_parts = [
        part.decode(encoding or "utf-8") if isinstance(part, bytes) else part
        for part, encoding in parts
    ]
    return "".join(decoded_parts)

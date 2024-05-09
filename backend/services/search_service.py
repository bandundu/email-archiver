# Services are used to interact with the database, perform business logic and other necesarry core functions. They are to be imported into the routes. Services should not use FastAPI's Request and Response classes. They should only return data to the routes. The routes will then use this data to return a response to the client.

import logging
import re
from dateutil import parser
import cachetools
import hashlib
from models.database import get_db
from models.models import Email
from sqlalchemy import func
from sqlalchemy import or_
import time


logger = logging.getLogger(__name__)

# Create a cache with a maximum size of 1000 and a TTL of 5 minutes
search_cache = cachetools.TTLCache(maxsize=1000, ttl=300)


def search_emails(query):
    start_time = time.time()

    logging.info(f"Searching for emails with query: {query}")

    # Generate a cache key based on the query
    cache_key = hashlib.sha256(query.encode()).hexdigest()

    # Check if the search results are already cached
    cached_results = search_cache.get(cache_key)
    if cached_results is not None:
        end_time = time.time()
        search_time = end_time - start_time
        logging.info("Returning cached search results.")
        return cached_results, search_time

    db = next(get_db())

    # Remove leading/trailing whitespaces and convert to lowercase
    query = query.strip().lower()

    # Check if the query is empty
    if not query:
        logging.info("Empty search query. Returning no results.")
        end_time = time.time()
        search_time = end_time - start_time
        return [], search_time

    # Check if the query contains a date range
    date_range_pattern = r"(\d{1,2}\s+\w{3}\s+\d{4})\s*-\s*(\d{1,2}\s+\w{3}\s+\d{4})"
    date_range_match = re.search(date_range_pattern, query)

    if date_range_match:
        start_date_str, end_date_str = date_range_match.groups()
        try:
            start_date = parser.parse(start_date_str, fuzzy=True).strftime("%Y-%m-%d")
            end_date = parser.parse(end_date_str, fuzzy=True).strftime("%Y-%m-%d")
            emails = (
                db.query(
                    Email.id,
                    Email.account_id,
                    Email.subject,
                    Email.sender,
                    Email.recipients,
                    Email.date,
                    Email.body,
                    Email.fingerprint,
                )
                .filter(Email.date >= start_date)
                .filter(Email.date <= end_date)
                .all()
            )
            logging.info(f"Found {len(emails)} emails within the date range.")
            search_cache[cache_key] = emails  # Cache the search results
            return emails
        except (ValueError, TypeError):
            logging.info("Invalid date range format. Proceeding with text search.")

    # Perform text search using the LIKE operator
    search_term = f"%{query}%"
    emails = (
        db.query(
            Email.id,
            Email.account_id,
            Email.subject,
            Email.sender,
            Email.recipients,
            Email.date,
            Email.body,
            Email.fingerprint,
        )
        .filter(
            or_(
                Email.subject.ilike(search_term),
                Email.sender.ilike(search_term),
                Email.recipients.ilike(search_term),
                Email.body.ilike(search_term),
            )
        )
        .all()
    )

    end_time = time.time()
    search_time = end_time - start_time

    logging.info(f"Found {len(emails)} emails matching the search query in {search_time} seconds.")
    search_cache[cache_key] = emails  # Cache the search results
    return emails, search_time

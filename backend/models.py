from typing import Optional
from pydantic import BaseModel

class AccountData(BaseModel):
    """
    Represents the data required to create or update an account.
    """
    email: str
    password: str
    protocol: str
    server: str
    port: int
    interval: int = 300
    selected_inboxes: Optional[list] = None

class SearchQuery(BaseModel):
    """
    Represents a search query for emails.
    """
    query: str
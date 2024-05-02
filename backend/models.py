from typing import Optional
from pydantic import BaseModel

class AccountData(BaseModel):
    email: str
    password: str
    protocol: str
    server: str
    port: int
    interval: int = 300
    selected_inboxes: Optional[list] = None

class SearchQuery(BaseModel):
    query: str
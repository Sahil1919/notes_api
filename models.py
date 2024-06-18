
from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    username: str
    password: str


class Note(BaseModel):
    title: str
    content: str
    shared_with: Optional[List[str]] = []


#use only for testing purpose
class ShareRequest(BaseModel):
    username: str
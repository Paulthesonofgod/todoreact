from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TaskIn(BaseModel):
    title: str

class Task(TaskIn):
    id: int
    completed: bool
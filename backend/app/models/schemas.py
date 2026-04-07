from pydantic import BaseModel, EmailStr

class AIQuerySchema(BaseModel):
    chat_id: str | None = None
    prompt: str


class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    username:str
    password:str

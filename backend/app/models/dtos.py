from dataclasses import dataclass
from fastapi import HTTPException


@dataclass
class RegisterDTO:
    username: str
    email: str
    password: str

    def __post_init__(self):
        self.username = self.username.strip()
        self.email = self.email.strip()
        self.password = self.password.strip()

        if not self.username:
            raise ValueError("Can't leave a blank username")

        if not self.email:
            raise ValueError("Can't leave a blank email")

        if len(self.password) < 8:
            raise ValueError("Password must be longer than 8 characters")


@dataclass
class LoginDTO:
    username:str
    password:str

    def __post_init__(self):
        self.username = self.username.strip()
        self.password = self.password.strip()

        if not self.username:
            raise ValueError("Can't leave a blank username")

        if len(self.password) < 8:
            raise ValueError("Password must be longer than 8 characters")
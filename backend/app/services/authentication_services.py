from datetime import timedelta, datetime, UTC
import uuid
from fastapi import HTTPException, status
from app.models.dtos import RegisterDTO, LoginDTO
from passlib.context import CryptContext
from app.core import settings
import jwt

class AuthenticationServices:
    def __init__(self, authentication_repository):
        self.authentication_repository = authentication_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = settings.jwt_algorithm
        self.private_key = settings.private_key
        self.public_key = settings.public_key


    async def register(self, register_body : RegisterDTO):
        existing_users = await self.authentication_repository.is_user_exist(username=register_body.username, email=register_body.email)
        if existing_users:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail= "User Already exists")
        hashed_password = self.pwd_context.hash(register_body.password)
        try:
            mongo_user_id = await self.authentication_repository.save_new_user(
                username= register_body.username,
                email=register_body.email,
                password=hashed_password
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        access_token = self.create_access_token(mongo_user_id)
        refresh_token = await self.create_refresh_token(mongo_user_id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


    async def login(self, login_body : LoginDTO):
        user = await self.authentication_repository.get_user_by_username(login_body.username)
        if not user:
            raise HTTPException(401, "Invalid username or password")

        is_password_verified = self.pwd_context.verify(login_body.password, user["password"])

        if not is_password_verified:
            raise HTTPException(401, "Invalid username or password")

        user_id_str = str(user["_id"])

        access_token = self.create_access_token(user_id_str)
        refresh_token = await self.create_refresh_token(user_id_str)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


    def create_access_token(self, user_id):
        payload = {
            "sub":str(user_id),
            "exp":datetime.now(UTC) + timedelta(minutes=15),
            "iat":datetime.now(UTC),
            "jti":str(uuid.uuid4()),
            "type": "access"
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)


    async def create_refresh_token(self, user_id):
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(UTC) + timedelta(days=7),
            "iat": datetime.now(UTC),
            "jti": str(uuid.uuid4()),
            "type": "refresh"
        }
        await self.authentication_repository.save_refresh_token(user_id, payload["jti"], payload["exp"])
        return jwt.encode(payload, self.private_key, self.algorithm)


    async def refresh_access_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.public_key, algorithms=[self.algorithm])

            if payload.get("type") != "refresh":
                raise HTTPException(401, "Invalid token type")

            user_id = payload.get("sub")
            jti = payload.get("jti")

            is_valid = await self.authentication_repository.is_refresh_token_valid(user_id, jti)
            if not is_valid:
                raise HTTPException(401, "Token revoked or expired")

            await self.authentication_repository.delete_refresh_token(jti)
            new_access_token = self.create_access_token(user_id)
            new_refresh_token = await self.create_refresh_token(user_id)
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Refresh token expired. Please log in again.")
        except jwt.PyJWTError:
            raise HTTPException(401, "Invalid refresh token")


    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(401, "Invalid token")
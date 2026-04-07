from fastapi import Depends, HTTPException, status, Request
from app.infrastructure.db import MongoManager,RedisManager
from app.infrastructure.repositories.authentication_repository import AuthenticationRepository
from app.services.authentication_services import AuthenticationServices
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings

security = HTTPBearer()


async def get_auth_repo(mongo_client: MongoManager = Depends(MongoManager.get_db)) -> AuthenticationRepository:
    return AuthenticationRepository(mongo_client)

async def get_auth_service(
    repo: AuthenticationRepository = Depends(get_auth_repo)
) -> AuthenticationServices:
    return AuthenticationServices(repo)


def get_token_and_verify(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme"
        )

    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing or invalid"
        )
    return token

def get_user_id(token):
    try:
        decoded_payload = jwt.decode(token, settings.public_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise ValueError("The token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token. The signature might be wrong or the token is malformed.")
    user_id = decoded_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme"
        )
    return user_id


async def rate_limit_login(request:Request, redis_client = Depends(RedisManager.get_client)):
    client_ip = request.client.host
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
    except Exception:
        email = "unknown_email"

    ip_key = f"rate_limit:login:ip:{client_ip}"
    email_key = f"rate_limit:login:email:{email}" if email != "unknown_email" else None

    pipe = redis_client.pipeline()

    pipe.incr(ip_key)
    if email_key:
        pipe.incr(email_key)

    results = await pipe.execute()

    ip_attempts = results[0]
    email_attempts = results[1] if email_key else 0

    if ip_attempts == 1:
        await redis_client.expire(ip_key, 60)
    if email_attempts == 1:
        await redis_client.expire(email_key, 300)

    if email_attempts > 5:
        step = (email_attempts - 6) // 2 + 1
        penalty = min(300 * (2 ** step), 86400)
        await redis_client.expire(email_key, penalty)
        ttl = await redis_client.ttl(email_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Please try again in {ttl} seconds",
            headers={"Retry-After": str(ttl)}
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_and_verify(credentials)
    try:
        return get_user_id(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
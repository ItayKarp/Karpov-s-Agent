from fastapi import APIRouter,Response, Depends, Cookie, HTTPException, status

from app.models.dtos import LoginDTO, RegisterDTO
from app.models.schemas import RegisterSchema, LoginSchema
from app.services.authentication_services import AuthenticationServices
from app.api.auth_dependencies import get_auth_service, rate_limit_login

auth_router = APIRouter(prefix="/auth")

@auth_router.post("/register")
async def register(
        body: RegisterSchema,
        response: Response,
        auth_service: AuthenticationServices = Depends(get_auth_service)
):
    try:
        dto = RegisterDTO(**body.model_dump())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid login credentials format or missing required fields."
        )
    tokens = await auth_service.register(dto)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age= 7 * 24 * 60 * 60
    )
    return {"access_token": tokens["access_token"], "token_type": "bearer"}


@auth_router.post("/login", dependencies=[Depends(rate_limit_login)])
async def login(
        body: LoginSchema,
        response: Response,
        auth_service: AuthenticationServices = Depends(get_auth_service)
):
    try:
        dto = LoginDTO(**body.model_dump())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid login credentials format or missing required fields."
        )

    tokens = await auth_service.login(dto)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age= 7 * 24 * 60 * 60
    )
    return {"access_token": tokens["access_token"], "token_type": "bearer"}

@auth_router.post("/refresh")
async def refresh(
        response: Response,
        refresh_token: str = Cookie(None),
        auth_service: AuthenticationServices = Depends(get_auth_service)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    tokens = await auth_service.refresh_access_token(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age= 7 * 24 * 60 * 60
    )

    return {"access_token": tokens["access_token"], "token_type": "bearer"}
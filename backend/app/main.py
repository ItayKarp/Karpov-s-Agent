from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.api.routers import auth_router, ai_router, chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X_Chat_Id"]
)
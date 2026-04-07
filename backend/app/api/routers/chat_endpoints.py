from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth_dependencies import get_current_user
from app.api.dependencies import get_chat_repo

chat_router = APIRouter(tags=["chats"])


@chat_router.get("/chats")
async def load_chats(
        user_id: str = Depends(get_current_user),
        chat_repo = Depends(get_chat_repo)
):
    return await chat_repo.get_chats(user_id)


@chat_router.get("/chat/{chat_id}")
async def load_chat(
        chat_id: str,
        user_id: str = Depends(get_current_user),
        chat_repo = Depends(get_chat_repo)
):
    return await chat_repo.get_chat(chat_id, user_id)


@chat_router.delete("/chat/{chat_id}")
async def delete_chat(
        chat_id: str,
        user_id: str = Depends(get_current_user),
        chat_repo = Depends(get_chat_repo)
):
    deleted = await chat_repo.delete_chat(chat_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return {"success": True}
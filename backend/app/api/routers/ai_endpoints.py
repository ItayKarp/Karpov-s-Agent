from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.models.schemas import AIQuerySchema
from app.api.dependencies import get_agent_orchestrator, get_chat_repo
from app.api.auth_dependencies import get_current_user
from app.orchestrator.agent_orchestrator import AgentOrchestrator


ai_router = APIRouter()

@ai_router.post("/chat")
async def ai_query(
        body: AIQuerySchema,
        user_id: str = Depends(get_current_user),
        agent_orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
) -> StreamingResponse:
    return await agent_orchestrator.run(user_id, body)


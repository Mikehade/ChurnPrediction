from fastapi import APIRouter, Request

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health(request: Request):
    return {
        "status": "running",
    }
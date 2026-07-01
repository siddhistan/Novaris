from fastapi import APIRouter
from pydantic import BaseModel

from backend.ai.generator import generate_code

router = APIRouter()


class Prompt(BaseModel):
    prompt: str


@router.post("/generate")
def generate(request: Prompt):

    return generate_code(request.prompt)
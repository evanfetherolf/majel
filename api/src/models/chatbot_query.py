from pydantic import BaseModel

class ChatbotInput(BaseModel):
    text: str

class ChatbotOutput(BaseModel):
    input: str
    output: str
    intermediate_steps: list[str]
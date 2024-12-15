from pydantic import BaseModel, Field

class StartCallRequest(BaseModel):
    phone_number: str = Field(..., regex=r"^\d{10,15}$")

class ProcessResponseRequest(BaseModel):
    call_id: int
    response_text: str
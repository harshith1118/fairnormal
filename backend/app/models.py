from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier for history tracking")
    message: str = Field(..., description="The user's query or message")

class Citation(BaseModel):
    reference: str = Field(..., description="Bible book, chapter, and verse cited")
    text: str = Field(..., description="Text of the scripture")
    verified: bool = Field(..., description="True if verified against canon, False if hallucination caught")

class ChatResponse(BaseModel):
    message: str = Field(..., description="The final assistant response")
    citations: List[Citation] = Field(default=[], description="List of scriptures cited in the response")
    safety_status: str = Field("ALLOW", description="Safety status: ALLOW, WARN, REFUSE")
    safety_reason: Optional[str] = Field(None, description="Reason for safety flag")

class ImageRequest(BaseModel):
    prompt: str = Field(..., description="A description of the Christian art to generate")
    style: str = Field("oil painting", description="Style, e.g., oil painting, digital art, sketch")
    enhance: bool = Field(True, description="True to auto-enhance prompt using Gemini LLM first")

class ImageResponse(BaseModel):
    image_url: Optional[str] = Field(None, description="Static image URL if stored")
    base64_image: Optional[str] = Field(None, description="Base64 data URL representing the image")
    enhanced_prompt: str = Field(..., description="The prompt used after LLM enhancement")
    safety_status: str = Field("ALLOW", description="ALLOW, REFUSE")
    safety_reason: Optional[str] = Field(None, description="Reason for safety flag")

class PreferenceRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    denomination: str = Field(..., description="Preferred denomination: Protestant, Catholic, Orthodox")

class PreferenceResponse(BaseModel):
    session_id: str
    denomination: str
    status: str

class HealthResponse(BaseModel):
    status: str
    chroma_status: str
    sqlite_status: str

class EvalRunRequest(BaseModel):
    test_id_subset: Optional[List[str]] = Field(None, description="Optional subset of test IDs to run")

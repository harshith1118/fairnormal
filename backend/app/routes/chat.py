from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse, Citation
from app.database import get_history, get_preference, save_message
from app.services.safety_service import SafetyService
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.verification_service import VerificationService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_msg = request.message
    
    # 1. Structured Safety Gateway check
    safety_check = SafetyService.evaluate_prompt(user_msg)
    if safety_check["status"] == "REFUSE":
        refusal_msg = "I cannot fulfill this request. To ensure doctrinal accuracy, safety, and respect, I do not generate content that manipulates scripture, contains hate speech, religious extremism, or references to violence."
        # Save refusal in database
        save_message(session_id, "user", user_msg)
        save_message(session_id, "assistant", refusal_msg)
        return ChatResponse(
            message=refusal_msg,
            citations=[],
            safety_status="REFUSE",
            safety_reason=safety_check["reason"]
        )

    # 2. Retrieve history and active denomination preference from SQLite
    history = get_history(session_id)
    denomination = get_preference(session_id)
    
    # 3. Retrieve relevant scriptures via ChromaDB RAG (denomination-aware)
    rag_results = RAGService.query_scriptures(user_msg, denomination=denomination, top_k=4)
    
    # 4. Formulate context and system instructions
    context_str = ""
    if rag_results:
        context_str = "Ground your answer in these retrieved scriptures from our database:\n"
        for v in rag_results:
            context_str += f"- {v['reference']} ({v['denomination'].upper()}): {v['text']}\n"
    else:
        context_str = "No specific verses retrieved. Ground your response in recognized biblical teaching.\n"
        
    system_instruction = (
        "You are FaithGuide AI, a Christianity-focused theological assistant.\n"
        "Your mission is to provide scripture-grounded answers, respect theological diversity, "
        "and maintain absolute scriptural accuracy.\n\n"
        f"The user has specified their theological preference as: {denomination}.\n"
        "Please follow these critical directives:\n"
        f"1. Primary Focus: Tailor your response to the {denomination} perspective. Provide the most depth here.\n"
        "2. Balanced Perspective: If significant theological differences exist on the topic, briefly mention the views of the other two major traditions (Protestant, Catholic, or Orthodox) to maintain objectivity. Keep these secondary views concise unless a comparison is explicitly requested.\n"
        "3. Precision: Quote scripture precisely and list references in standard form (e.g., John 3:16).\n"
        "4. No Hallucinations: DO NOT invent or fabricate any bible book, chapter, or verse. If uncertain, say 'I cannot verify that information.'\n"
        "5. Safety: Under no circumstances generate hate speech, violence, or doctrinal manipulation."
    )
    
    full_prompt = f"Context:\n{context_str}\n\nUser Question:\n{user_msg}"
    
    # 5. Generate LLM generation response
    raw_response = LLMService.generate_chat_response(
        prompt=full_prompt,
        system_instruction=system_instruction
    )
    
    # 6. Post-generation Scripture Verification Layer (detect and strip hallucinations)
    sanitized_response, citations_logged = await VerificationService.intercept_and_verify(raw_response)
    
    # Convert dict citations to Citation pydantic models
    citations = [
        Citation(reference=c["reference"], text=c["text"], verified=c["verified"])
        for c in citations_logged
    ]
    
    # 7. Persist messages to SQLite conversation logs
    save_message(session_id, "user", user_msg)
    save_message(session_id, "assistant", sanitized_response)
    
    return ChatResponse(
        message=sanitized_response,
        citations=citations,
        safety_status=safety_check["status"],
        safety_reason=safety_check["reason"]
    )

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from src.deploy.model_loader import ModelLoader

# app = FastAPI(title="Local Finance AI API")

# class ChatRequest(BaseModel):
#     prompt: str

# @app.get("/")
# def health_check():
#     return {"status": "online", "model": "TinyLlama-Finance-GGUF"}

# @app.post("/chat")
# def chat(request: ChatRequest):
#     try:
#         llm = ModelLoader.get_model()
        
#         # Simple prompt template
#         formatted_prompt = f"Instruction: {request.prompt}\nResponse:"
        
#         output = llm(formatted_prompt, max_tokens=128, temperature=0.7)
#         return {"answer": output["choices"][0]["text"].strip()}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.deploy.model_loader import ModelLoader

app = FastAPI(title="Local Finance AI API")

# Data Models
class GenerateRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    prompt: str
    system_prompt: str = "You are a helpful financial advisor."

# 1. Health Check (To see if server is alive)
@app.get("/")
def health_check():
    return {"status": "online", "model": "TinyLlama-Finance-GGUF"}

# 2. Raw Generation Endpoint
@app.post("/generate")
def generate(request: GenerateRequest):
    try:
        llm = ModelLoader.get_model()
        formatted_prompt = f"Instruction: {request.prompt}\nResponse:"
        output = llm(formatted_prompt, max_tokens=128, temperature=0.7)
        return {"answer": output["choices"][0]["text"].strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    #     output = llm(request.prompt, max_tokens=request.max_tokens)
    #     return {"result": output["choices"][0]["text"].strip()}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

# 3. Structured Chat Endpoint
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        llm = ModelLoader.get_model()
        
        # Wrapping user prompt in a financial instruction template
        full_prompt = f"System: {request.system_prompt}\nUser: {request.prompt}\nAssistant:"
        
        output = llm(full_prompt, max_tokens=150, temperature=0.7)
        return {"answer": output["choices"][0]["text"].strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
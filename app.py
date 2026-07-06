from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import uvicorn

from llm.client import extract_arguments, check_ollama_status
from core.graph import build_graph, detect_gaps

app = FastAPI(title="MaizeMind")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "MaizeMind API is running", "status": "ok"}

@app.post("/analyze")
async def analyze_text(data: TextInput):
    try:
        if not data.text or len(data.text.strip()) < 10:
            return JSONResponse(
                status_code=400,
                content={"error": "Please enter at least 10 characters"}
            )
        
        # Extract arguments
        arguments = extract_arguments(data.text)
        
        # Build graph
        graph_data = build_graph(arguments)
        
        # Detect gaps
        gaps = detect_gaps(graph_data)
        
        return {
            "success": True,
            "graph": graph_data,
            "gaps": gaps,
            "message": f"Found {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} relationships"
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/sample")
async def get_sample():
    sample = """Social media has a negative impact on mental health. 
    Studies show that excessive social media use leads to increased anxiety and depression. 
    A 2022 study found that teens who spend more than 3 hours per day on social media are 60% more likely to report mental health issues. 
    However, some argue that social media helps people stay connected, especially during lockdowns. 
    Research from the University of Oxford suggests that moderate use (under 2 hours) can actually reduce feelings of loneliness."""
    
    return {"sample_text": sample}

if __name__ == "__main__":
    print("🚀 Starting MaizeMind API...")
    print("📱 Visit http://localhost:8000")
    is_running, message = check_ollama_status()
    print(message)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
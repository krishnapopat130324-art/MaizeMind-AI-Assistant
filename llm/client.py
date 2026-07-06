import requests
import json
import time
import re

def query_ollama(prompt, model="llama3.2:1b", temperature=0.1, max_retries=3):
    """
    Send a prompt to the local Ollama instance and get a response.
    
    Args:
        prompt (str): The prompt to send to the LLM
        model (str): The model name (default: llama3.2:1b)
        temperature (float): Sampling temperature (0.0-1.0)
        max_retries (int): Number of retry attempts on failure
    
    Returns:
        str: The LLM's response text
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "max_tokens": 2000,
        "top_p": 0.9
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            if "response" in result:
                return result["response"]
            else:
                return f"Error: Unexpected response format from Ollama: {result}"
                
        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                return """Error: Could not connect to Ollama. 
Please make sure:
1. Ollama is installed
2. Run 'ollama serve' in a terminal
3. The model 'llama3.2:1b' is downloaded (run 'ollama pull llama3.2:1b')"""
            time.sleep(2)
            
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return "Error: Ollama request timed out. Please try again."
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                return f"Error: {str(e)}"
            time.sleep(2)
    
    return "Error: Failed to get response from Ollama after multiple attempts."

def get_available_models():
    """
    Get a list of available models from Ollama.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except:
        return []

def check_ollama_status():
    """
    Check if Ollama is running and accessible.
    Returns (bool, str): (is_running, message)
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            if "llama3.2:1b" in model_names:
                return True, "✅ Ollama is running with llama3.2:1b model"
            elif "llama3.2" in model_names:
                return True, "✅ Ollama is running with llama3.2 model"
            elif model_names:
                return True, f"✅ Ollama is running with models: {', '.join(model_names[:3])}"
            else:
                return True, "⚠️ Ollama is running but no models found. Run 'ollama pull llama3.2:1b'"
    except:
        return False, "❌ Ollama is not running. Start with 'ollama serve'"
    
    return False, "❌ Unknown status"

def extract_arguments(text):
    """
    Extract arguments from text using the LLM.
    Optimized for llama3.2:1b model.
    """
    prompt = f"""You are an argument extraction expert. Analyze the text and extract claims, evidence, and relationships.

Text: {text}

Return ONLY valid JSON. No other text. Use this exact format:
{{"claims":[{{"id":"C1","text":"claim text","type":"main"}}],"evidence":[{{"id":"E1","text":"evidence text","supports":"C1"}}],"relationships":[{{"source":"E1","target":"C1","type":"supports"}}]}}

Rules:
- Claims: Main points the author is trying to prove
- Evidence: Facts, data, or examples that support claims
- Types: "main", "supporting", "counter", "conclusion"
- For evidence, "supports" must reference a claim ID
- Find at least 2-3 claims and 1-2 evidence pieces if possible

Return ONLY JSON:"""

    response = query_ollama(prompt)
    
    # Try to extract JSON
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            if "claims" in result and "evidence" in result and "relationships" in result:
                return result
        except:
            pass
    
    # Try direct parsing
    try:
        result = json.loads(response)
        if "claims" in result and "evidence" in result and "relationships" in result:
            return result
    except:
        pass
    
    # Fallback: Create structure from text
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
    claims = []
    evidence = []
    relationships = []
    
    if sentences:
        # First sentence as main claim
        claims.append({"id": "C1", "text": sentences[0][:150], "type": "main"})
        
        # Next sentences as supporting claims or evidence
        for i, sentence in enumerate(sentences[1:], start=2):
            if i <= 4:
                if "study" in sentence.lower() or "research" in sentence.lower() or "found" in sentence.lower() or "report" in sentence.lower() or "data" in sentence.lower():
                    evidence.append({"id": f"E{i-1}", "text": sentence[:150], "supports": "C1"})
                    relationships.append({"source": f"E{i-1}", "target": "C1", "type": "supports"})
                else:
                    claims.append({"id": f"C{i}", "text": sentence[:150], "type": "supporting"})
                    relationships.append({"source": f"C{i}", "target": "C1", "type": "supports"})
    
    # If no evidence found, try to find evidence in text
    if not evidence:
        for sentence in sentences:
            if any(word in sentence.lower() for word in ["study", "research", "found", "report", "data", "shows", "proves", "demonstrates"]):
                evidence.append({"id": f"E{len(evidence)+1}", "text": sentence[:150], "supports": "C1"})
                relationships.append({"source": f"E{len(evidence)}", "target": "C1", "type": "supports"})
    
    return {
        "claims": claims if claims else [{"id": "C1", "text": "Could not extract arguments. Try again with clearer text.", "type": "main"}],
        "evidence": evidence,
        "relationships": relationships
    }
import json
import re
from llm.client import query_ollama

def extract_arguments(text):
    """
    Extract claims, evidence, and relationships from user text.
    Improved version with better fallback extraction.
    """
    
    # First, try to use the LLM
    prompt = f"""You are an argument extraction expert. Analyze the text and extract ALL claims, evidence, and relationships.

Text: {text}

Return ONLY valid JSON. No other text. Use this exact format:
{{"claims":[{{"id":"C1","text":"claim text","type":"main"}},{{"id":"C2","text":"claim text","type":"supporting"}}],"evidence":[{{"id":"E1","text":"evidence text","supports":"C1"}}],"relationships":[{{"source":"E1","target":"C1","type":"supports"}}]}}

IMPORTANT RULES:
1. Find ALL main claims and supporting claims
2. Find ALL evidence that supports claims
3. If you see words like "study", "research", "found", "shows" - that's evidence
4. Look for counter-arguments too (words like "however", "some argue")
5. Create relationships between evidence and claims
6. Return AT LEAST 3-4 claims and 2-3 evidence pieces if available

Return ONLY JSON:"""

    try:
        response = query_ollama(prompt, model="llama3.2:1b", temperature=0.1)
        
        # Try to parse JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                if "claims" in result and "evidence" in result and "relationships" in result:
                    # Make sure we have enough items
                    if len(result["claims"]) >= 2 and len(result["evidence"]) >= 1:
                        return result
            except:
                pass
        
        # If LLM fails, use our smart fallback
        return smart_extract(text)
        
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        return smart_extract(text)

def smart_extract(text):
    """
    Smart fallback extraction that manually finds claims and evidence.
    This ensures we always get detailed output.
    """
    # Split into sentences
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    
    claims = []
    evidence = []
    relationships = []
    
    # Keywords that indicate evidence
    evidence_keywords = ['study', 'research', 'found', 'report', 'data', 'shows', 
                         'proves', 'demonstrates', 'according to', 'survey', 
                         'analysis', 'statistics', 'percent', '%', 'published']
    
    # Keywords that indicate counter-arguments
    counter_keywords = ['however', 'but', 'although', 'though', 'yet', 
                        'some argue', 'opponents', 'critics', 'nevertheless']
    
    # Keywords that indicate conclusions
    conclusion_keywords = ['therefore', 'thus', 'hence', 'consequently', 
                          'as a result', 'in conclusion', 'overall']
    
    # First pass: Identify main claim (usually first sentence)
    if sentences:
        claims.append({
            "id": "C1",
            "text": sentences[0][:200],
            "type": "main"
        })
    
    # Second pass: Process each sentence
    for i, sentence in enumerate(sentences[1:], start=2):
        sentence_lower = sentence.lower()
        
        # Skip very short sentences
        if len(sentence) < 15:
            continue
            
        # Check if it's evidence
        is_evidence = any(keyword in sentence_lower for keyword in evidence_keywords)
        
        # Check if it's a counter-argument
        is_counter = any(keyword in sentence_lower for keyword in counter_keywords)
        
        # Check if it's a conclusion
        is_conclusion = any(keyword in sentence_lower for keyword in conclusion_keywords)
        
        if is_evidence:
            # This is evidence
            evidence_id = f"E{len(evidence) + 1}"
            evidence.append({
                "id": evidence_id,
                "text": sentence[:200],
                "supports": "C1"  # Supports main claim by default
            })
            relationships.append({
                "source": evidence_id,
                "target": "C1",
                "type": "supports"
            })
        elif is_counter:
            # This is a counter-claim
            claim_id = f"C{len(claims) + 1}"
            claims.append({
                "id": claim_id,
                "text": sentence[:200],
                "type": "counter"
            })
            relationships.append({
                "source": claim_id,
                "target": "C1",
                "type": "challenges"
            })
        elif is_conclusion:
            # This is a conclusion claim
            claim_id = f"C{len(claims) + 1}"
            claims.append({
                "id": claim_id,
                "text": sentence[:200],
                "type": "conclusion"
            })
            relationships.append({
                "source": claim_id,
                "target": "C1",
                "type": "supports"
            })
        else:
            # Regular supporting claim
            claim_id = f"C{len(claims) + 1}"
            claims.append({
                "id": claim_id,
                "text": sentence[:200],
                "type": "supporting"
            })
            relationships.append({
                "source": claim_id,
                "target": "C1",
                "type": "supports"
            })
    
    # If we have too few claims, add some from the text
    if len(claims) < 2:
        for i, sentence in enumerate(sentences[:3], start=2):
            if len(sentence) > 15:
                claims.append({
                    "id": f"C{i}",
                    "text": sentence[:200],
                    "type": "supporting"
                })
                relationships.append({
                    "source": f"C{i}",
                    "target": "C1",
                    "type": "supports"
                })
    
    # If we have no evidence, try to find some
    if not evidence:
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in evidence_keywords):
                evidence.append({
                    "id": f"E{len(evidence) + 1}",
                    "text": sentence[:200],
                    "supports": "C1"
                })
                relationships.append({
                    "source": f"E{len(evidence)}",
                    "target": "C1",
                    "type": "supports"
                })
                break
    
    return {
        "claims": claims if claims else [
            {"id": "C1", "text": "Could not extract arguments. Try again.", "type": "main"}
        ],
        "evidence": evidence,
        "relationships": relationships
    }

def format_arguments_for_display(arguments):
    """Format extracted arguments for display in the UI"""
    result = []
    
    for claim in arguments.get("claims", []):
        result.append({
            "type": "claim",
            "id": claim.get("id", "unknown"),
            "text": claim.get("text", ""),
            "subtype": claim.get("type", "unknown")
        })
    
    for evidence in arguments.get("evidence", []):
        result.append({
            "type": "evidence",
            "id": evidence.get("id", "unknown"),
            "text": evidence.get("text", ""),
            "supports": evidence.get("supports", "unknown")
        })
    
    return result
import os
import random
import pandas as pd
import requests
from transformers import pipeline  # For local LLM fallback
from dotenv import load_dotenv

load_dotenv()

# ===== 1. First define all helper functions =====
def get_answer_type(query):
    """Categorize user query for offline responses"""
    query = query.lower()
    if any(word in query for word in ["hello", "hi", "hey"]):
        return "greeting"
    elif any(word in query for word in ["waste", "quantity", "total"]):
        return "waste_stats"
    elif any(word in query for word in ["tip", "reduce", "prevent"]):
        return "tips"
    elif any(word in query for word in ["sustain", "planet", "eco"]):
        return "sustainability"
    return "fallback"

def generate_data_specific_response(query, waste_data):
    """Generate responses based on waste data analysis"""
    if waste_data is None or waste_data.empty:
        return None
        
    query = query.lower()
    try:
        if "total waste" in query:
            total = waste_data["quantity_kg"].sum()
            return f"Total recorded waste: {total:.2f} kg"
            
        elif "most wasted" in query:
            if "category" in waste_data.columns:
                top = waste_data.groupby("category")["quantity_kg"].sum().idxmax()
                return f"Most wasted category: {top}"
                
        elif "average" in query:
            if "date" in waste_data.columns:
                avg = waste_data.groupby("date")["quantity_kg"].sum().mean()
                return f"Average daily waste: {avg:.2f} kg"
                
    except Exception as e:
        print(f"Data analysis error: {e}")
    return None

# ===== 2. Then define constants =====
responses = {
    "greeting": ["Hello! How can I help with food waste today?"],
    "waste_stats": ["Here's what I know about your waste patterns..."],
    "tips": ["Try meal planning to reduce waste!"],
    "sustainability": ["Food waste reduction helps the planet!"],
    "fallback": ["I'm not sure I understand. Ask about waste stats or tips!"]
}

# ===== 3. Finally define main chatbot function =====
def get_chatbot_response(query, waste_data=None):
    """Main function to generate responses with fallback logic"""
    MODE = os.getenv("CHATBOT_MODE", "auto")
    
    # 1. Try data-specific response first
    if waste_data is not None:
        data_response = generate_data_specific_response(query, waste_data)
        if data_response:
            return data_response
    
    # 2. Try API/local LLM if in online mode
    if MODE != "offline":
        # DeepSeek API attempt
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key and MODE == "online":
            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{
                            "role": "system",
                            "content": "You're a food waste expert assistant."
                        }, {
                            "role": "user",
                            "content": query
                        }],
                        "temperature": 0.7,
                        "max_tokens": 300
                    }
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                pass
        
        # Local LLM fallback
        try:
            if not hasattr(get_chatbot_response, 'llm'):
                get_chatbot_response.llm = pipeline(
                    "text-generation",
                    model="gpt2",
                    device="cpu"
                )
            result = get_chatbot_response.llm(
                f"Food waste question: {query}\nAnswer:",
                max_length=100,
                temperature=0.7
            )
            return result[0]['generated_text'].split("Answer:")[-1].strip()
        except Exception as e:
            print(f"LLM error: {e}")
    
    # 3. Final offline fallback
    return random.choice(responses[get_answer_type(query)])
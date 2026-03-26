from typing import Optional
import os
from openai import OpenAI
from src.helpers.normalize_models import normalize_model, normalize_models
from src.utils.env import load_env

OPENAI_MODEL_MAP = {
    "chatgpt": "gpt-4o-mini",
    "gpt4": "gpt-4o",
    "gpt4o": "gpt-4o",
    "gptmini": "gpt-4o-mini"
}

load_env()
api_key = os.getenv("OPENAI_API_KEY", "").strip()

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Did you call load_env()?")

_openai_client = OpenAI(api_key=api_key)

print("LOADED model_apis FROM:", __file__)

def get_answer_gemini(model: str, question: str) -> str:
    #Placeholder for gemini API
    raise NotImplementedError("Gemini API not implemented.")

def get_answer_deepseek(model: str, question: str) -> str:
    #Placeholder for gemini
    raise NotImplementedError("DeepSeek API is not implemented.")

def get_answer_openai(model: str, question: str) -> str:
    key = normalize_model(model) 
    api_model = OPENAI_MODEL_MAP.get(key, "gpt-4o-mini")
    DEBUG = False
    if DEBUG:
        print(f"[DEBUG] model={model} key={key} api_model={api_model}")
    
    response = _openai_client.chat.completions.create(
        model=api_model,
        messages=[{"role": "user", "content": question}],
        temperature=0.0,
)
    return (response.choices[0].message.content or "").strip()  # type: ignore

'''def fake_get_answer(model: str, question: str) -> str:
    """
    Lažna funkcija za testiranje bez API ključeva.
    Vraća različite odgovore zavisno od modela da simulira razlike.
    """
    #Normalizujemo ulaz na nepotrebne karaktere
    key = normalize_model(model)
    
    # Simuliramo različite stilove odgovora
    responses = {
        "gemini": f"According to medical guidelines, {question} The answer involves liver function and glucose metabolism.",
        "deepseek": f"Clinical response: {question} Mechanism: decreases hepatic glucose production.",
        "claude": f"Medical analysis: {question} Effect: reduces liver glucose output and improves insulin sensitivity.",
        "perplexity": f"Sourced from literature: {question} Key mechanism: inhibition of hepatic glucose release.",
        "copilot": f"Healthcare insight: {question} Function: lowers blood glucose via hepatic pathway.",
        "gpt4": f"GPT-4 analysis: {question} Advanced reasoning indicates hepatic glucose suppression.",
        "chatgpt": f"ChatGPT response: {question} According to OpenAI's model, the mechanism involves...",
    }
    
    # Return answer for requested model, or default
    return responses.get(key, f"Generic answer for: {question}")'''
    
def get_answer_fn(model: str, question: str) -> str:
    key = normalize_model(model)
    
    #OpenAI
    if key in {"chatgpt", "gpt4", "gpt4o", "gptmini"}:
        return get_answer_openai(model, question)
    
    #Ostali
    if key.startswith("gemini"):
        return get_answer_gemini(model, question)

    if key.startswith("deepseek"):
        return get_answer_deepseek(model, question)

    raise NotImplementedError(f"Model routing not implemented for: {model} (key={key})")


if __name__ == "__main__":
    #Test funk
    print(normalize_model("GPT-4"))        # gpt4
    print(normalize_model("Gemini Pro"))   # geminipro
    print(normalize_model("claude-3.5"))   # claude35
    print(normalize_model("perplexity"))  
    print(normalize_model("copilot"))   
    print(normalize_model("chatgpt"))   
    
    
    print(normalize_models(["GPT-4", "Gemini Pro", "  claude  "]))
    
    # Test get_answer_fn
    print("\n=== Test get_answer_fn ===")
    question = "What is metformin?"
    
    all_models = ["ChatGPT", "Gemini", "Claude", "Perplexity", "DeepSeek", "CoPilot", "GPT-4"]
    
    for model in all_models:
        answer = get_answer_fn(model, question)
        key = normalize_model(model)
        print(f"{model:12} → {key:15}: {answer[:40]}...")

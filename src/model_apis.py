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


# DEBUG moved to module level (global variable),
DEBUG = False

print("LOADED model_apis FROM:", __file__)


def get_answer_gemini(model: str, question: str) -> str:
    # Placeholder for Gemini API
    raise NotImplementedError("Gemini API not implemented.")


def get_answer_deepseek(model: str, question: str) -> str:
    # Placeholder for DeepSeek API
    raise NotImplementedError("DeepSeek API is not implemented.")


def get_answer_openai(model: str, question: str) -> str:
    key = normalize_model(model)
    api_model = OPENAI_MODEL_MAP.get(key, "gpt-4o-mini")

    if DEBUG:
        print(f"[DEBUG] model={model} key={key} api_model={api_model}")

    response = _openai_client.chat.completions.create(
        model=api_model,
        messages=[{"role": "user", "content": question}],
        temperature=0.0,
    )
    return (response.choices[0].message.content or "").strip()  # type: ignore


def get_answer_fn(model: str, question: str) -> str:
    key = normalize_model(model)

    # OpenAI
    if key in {"chatgpt", "gpt4", "gpt4o", "gptmini"}:
        return get_answer_openai(model, question)

    # Other providers
    if key.startswith("gemini"):
        return get_answer_gemini(model, question)

    if key.startswith("deepseek"):
        return get_answer_deepseek(model, question)

    raise NotImplementedError(f"Model routing not implemented for: {model} (key={key})")


if __name__ == "__main__":
    # Test normalize functions
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
        # `key` is now defined at the start of each iteration, before it is used in the print statement.
        key = normalize_model(model)

        try:
            answer = get_answer_fn(model, question)
            print(f"{model:12} → {key:15}: {answer[:40]}...")
        except NotImplementedError as e:
            print(f"{model:12} → {key:15}: NOT IMPLEMENTED — {e}")
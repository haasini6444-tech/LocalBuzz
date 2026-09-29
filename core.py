import os, re, time
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

MODELS = ["openai/gpt-oss-120b", "qwen/qwen3-32b"]  # main model, then backup

llm = Groq(api_key=os.environ["GROQ_API_KEY"])
def get_memory_client():
    """Create a fresh client each time, to avoid cross-thread reuse issues on Streamlit Cloud."""
    return Hindsight(
        base_url=os.environ["HINDSIGHT_URL"],
        api_key=os.environ["HINDSIGHT_API_KEY"],
    )

def ask_llm(system_prompt, user_prompt, retries=3):
    """Call Groq; retry, then fall back to the second model on errors."""
    for attempt in range(retries):
        for model in MODELS:
            try:
                r = llm.chat.completions.create(
                    model=model,
                    temperature=0.4,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                text = r.choices[0].message.content or ""
                # some models print their reasoning inside <think> tags
                return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            except Exception as e:
                print(f"[LLM error with {model}] {e}")
        time.sleep(2 * (attempt + 1))
    return "⚠️ The AI service is busy right now. Please try again in a moment."
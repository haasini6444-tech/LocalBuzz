import os
from dotenv import load_dotenv
load_dotenv()

print("Groq key found:", bool(os.getenv("GROQ_API_KEY")))
print("Hindsight key found:", bool(os.getenv("HINDSIGHT_API_KEY")))
print("Hindsight URL:", os.getenv("HINDSIGHT_URL"))
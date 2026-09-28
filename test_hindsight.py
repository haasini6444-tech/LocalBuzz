import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
load_dotenv()

client = Hindsight(
    base_url=os.environ["HINDSIGHT_URL"],
    api_key=os.environ["HINDSIGHT_API_KEY"],
)

# STORE a memory
client.retain(
    bank_id="customer-101",
    content="Ravi uses Windows 11 and Chrome. His WiFi drops every evening.",
)
print("Stored!")

# SEARCH memories
results = client.recall(
    bank_id="customer-101",
    query="What device does Ravi use?",
)
for r in results.results:
    print("-", r.text)
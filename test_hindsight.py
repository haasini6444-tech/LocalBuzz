import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
load_dotenv()

client = Hindsight(
    base_url=os.environ["HINDSIGHT_URL"],
    api_key=os.environ["HINDSIGHT_API_KEY"],
)

results = client.recall(
    bank_id="biz-sweet-crumbs-bakery",
    query="posts and engagement",
)
print("Number of results:", len(results.results))
for r in results.results:
    print("-", r.text)
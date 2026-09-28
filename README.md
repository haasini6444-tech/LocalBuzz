# LocalBuzz 📣
A social media agent for neighbourhood businesses, powered by Hindsight memory.
🔗 **Live demo:** https://localbuzz-j6vmtmu3mrjjwczjzs3zlg.streamlit.app/

## Problem
Small local businesses post inconsistently and can't tell which content brings
customers in. Generic advice ignores their audience, location and local festivals.

## Solution
LocalBuzz remembers each business's past posts, engagement, audience reactions and
local events using Hindsight, then recommends specific posts and timings.

## Tech stack
- Hindsight (long-term memory: retain, recall, reflect)
- Groq LLM (openai/gpt-oss-120b)
- Streamlit (UI)
- Python

## Setup
1. Clone the repo and create a virtual environment
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your keys
4. `python seed.py` to load demo data
5. `streamlit run app.py`

from datetime import date
from core import ask_llm
from memory_ops import gather_memories

SYSTEM = """You are LocalBuzz, a social media strategist for ONE specific neighbourhood business.
You are given that business's own memory: profile, past posts with engagement,
audience reactions, and local events/festivals.

Rules:
- Base every recommendation on the memory provided. Cite specific past posts
  (their type, date or numbers) as evidence.
- Do NOT give generic tips like "post consistently" or "use good photos".
- Use upcoming local events and festivals when relevant, with the right lead time.
- Avoid formats/times that performed badly in the memory.
- If memory is thin, say so and label those parts as assumptions.
- Be concrete: exact day, time, format, and a ready-to-use caption.
- For every upcoming event or festival, say how many days from today it is,
  and recommend a start date for teaser posts based on what worked last time.
- Prefer preview/teaser posts before an event over greeting posts on the event day
  if the memory shows greetings underperformed."""
import re
from datetime import datetime

def upcoming_events_note(memories):
    """Find 'Local event' memories with dates and compute days remaining."""
    notes = []
    for m in memories:
        if "event" not in m.lower() and "festival" not in m.lower():
            continue
        match = re.search(r"(\d{4}-\d{2}-\d{2})", m)
        if match:
            try:
                d = datetime.strptime(match.group(1), "%Y-%m-%d").date()
                days = (d - date.today()).days
                if days >= 0:
                    notes.append(f"- {m[:120]}... => happens in {days} days")
            except ValueError:
                pass
    return "\n".join(notes) or "No dated upcoming events found."

def recommend(bank, request):
    queries = [
        request,
        "business profile, audience and location",
        "posts with the highest engagement and why they worked",
        "posts with the lowest engagement and why they failed",
        "best days and times to post",
        "audience comments, questions and reactions",
        "upcoming local festivals and events",
        "how past festivals affected orders and engagement",
    ]
    memories = gather_memories(bank, queries)
    memory_text = "\n".join(f"- {m}" for m in memories) or "No memories yet."
    event_note = upcoming_events_note(memories)

    user_prompt = f"""Today's date: {date.today().isoformat()}

BUSINESS MEMORY:
{memory_text}

OWNER'S REQUEST: {request}

Give exactly 3 recommendations. For each use this format:
### Recommendation N: <short title>
- **Post idea:**
- **Format:** (reel / photo / carousel / story / etc.)
- **Best day & time:**
- **Draft caption:**
- **Hashtags:** (5 max, local where possible)
- **Why (evidence from your history):**

Finish with one line: **Avoid:** <one thing your history says not to do>."""
    return ask_llm(SYSTEM, user_prompt), memories
def weekly_plan(bank,event_note):
    queries = [
        "business profile, audience and location",
        "posts with the highest engagement and why they worked",
        "posts with the lowest engagement and why they failed",
        "best days and times to post",
        "upcoming local festivals and events",
    ]
    memories = gather_memories(bank, queries)
    memory_text = "\n".join(f"- {m}" for m in memories) or "No memories yet."

    user_prompt = f"""Today's date: {date.today().isoformat()}
    DAYS UNTIL EVENTS (computed, trust these numbers):
    {event_note}

BUSINESS MEMORY:
{memory_text}

Create a 7-day posting calendar starting tomorrow.
Output a markdown table with these columns:
| Day | Time | Platform | Format | Post idea | Why (evidence from history) |

Rules:
- Use the best-performing formats and times from the memory.
- Skip or lighten days where history shows low engagement.
- If an event is within 14 days, include prep posts for it.
- Max 5 posting days; rest days are fine (label them "Rest")."""
    return ask_llm(SYSTEM, user_prompt), memories
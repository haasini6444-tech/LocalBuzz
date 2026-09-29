import re
from datetime import date, datetime
from core import ask_llm, memory
from memory_ops import gather_memories

SYSTEM = """You are LocalBuzz, a social media strategist for ONE specific neighbourhood business.
You are given that business's own memory: profile, past posts with engagement,
audience reactions, and local events/festivals.

CRITICAL RULE ABOUT EVIDENCE:
- Only cite a specific post, number, or reaction if it actually appears in the
  memory given to you below. NEVER invent or assume evidence that isn't there.
- If the memory is empty or very thin (fewer than 2 relevant items), you MUST
  start your answer with a clear line: "I don't have much history for this
  business yet, so these are general best practices, not personalized advice."
  Then give general, clearly-labeled starter tips instead of fabricated
  evidence-based ones.
- If memory IS present, use it and cite it specifically (post type, date, numbers).

Other rules:
- Do NOT give generic tips like "post consistently" or "use good photos" when
  you DO have real history to draw from instead.
- Use upcoming local events and festivals when relevant, with the right lead time.
- Avoid formats or times that performed badly in the memory.
- Be concrete: exact day, time, format, and a ready-to-use caption."""


def upcoming_events_note(memories):
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
                    notes.append(f"- {m[:120]}... happens in {days} days")
            except ValueError:
                pass
    return "\n".join(notes) if notes else "No dated upcoming events found."


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
    is_cold_start = len(memories) < 2
    memory_text = "\n".join(f"- {m}" for m in memories) if memories else "No memories yet."
    event_note = upcoming_events_note(memories)

    cold_start_note = ""
    if is_cold_start:
        cold_start_note = (
            "\n\nIMPORTANT: This business has little to no history. "
            "You MUST open your answer with the warning line about limited "
            "history, and give general starter advice, not fabricated evidence."
        )

    user_prompt = (
        f"Today's date: {date.today().isoformat()}\n\n"
        f"BUSINESS MEMORY:\n{memory_text}\n\n"
        f"DAYS UNTIL EVENTS (computed, trust these numbers):\n{event_note}\n"
        f"{cold_start_note}\n\n"
        f"OWNER'S REQUEST: {request}\n\n"
        "Give exactly 3 recommendations. For each use this format:\n"
        "### Recommendation N: <short title>\n"
        "- Post idea:\n"
        "- Format: (reel / photo / carousel / story / etc.)\n"
        "- Best day and time:\n"
        "- Draft caption:\n"
        "- Hashtags: (5 max, local where possible)\n"
        "- Why (evidence from your history):\n\n"
        "Finish with one line: Avoid: <one thing your history says not to do>."
    )

    answer = ask_llm(SYSTEM, user_prompt)
    return answer, memories, is_cold_start


def weekly_plan(bank):
    queries = [
        "business profile, audience and location",
        "posts with the highest engagement and why they worked",
        "posts with the lowest engagement and why they failed",
        "best days and times to post",
        "upcoming local festivals and events",
    ]
    memories = gather_memories(bank, queries)
    memory_text = "\n".join(f"- {m}" for m in memories) if memories else "No memories yet."

    user_prompt = (
        f"Today's date: {date.today().isoformat()}\n\n"
        f"BUSINESS MEMORY:\n{memory_text}\n\n"
        "Create a 7-day posting calendar starting tomorrow.\n"
        "Output a markdown table with these columns:\n"
        "| Day | Time | Platform | Format | Post idea | Why (evidence from history) |\n\n"
        "Rules:\n"
        "- Use the best-performing formats and times from the memory.\n"
        "- Skip or lighten days where history shows low engagement.\n"
        "- If an event is within 14 days, include prep posts for it.\n"
        "- Max 5 posting days; rest days are fine (label them Rest)."
    )
    return ask_llm(SYSTEM, user_prompt), memories


def proactive_nudge(bank):
    try:
        insight = memory.reflect(
            bank_id=bank,
            query=(
                "Looking at all posts, engagement, audience reactions and "
                "timing patterns, what is the single most useful, specific, "
                "non-obvious pattern this business owner should know right now? "
                "If there is an upcoming festival or event, factor it in. "
                "Answer in ONE short sentence, like a helpful nudge, starting "
                "with an emoji. If there isn't enough history for a real "
                "pattern, say so honestly in one sentence instead."
            ),
        )
        return insight.text.strip()
    except Exception as e:
        print(f"[nudge error] {e}")
        return None
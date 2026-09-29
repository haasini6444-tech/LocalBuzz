import os
import re
import json
import time
from core import get_memory_client

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def bank_for(business_name):
    slug = re.sub(r"[^a-z0-9]+", "-", business_name.lower()).strip("-")
    return f"biz-{slug}"


def _pad_time(time_str):
    """Ensure HH:MM has zero-padded hour and minute, e.g. '4:0' -> '04:00'."""
    try:
        parts = time_str.strip().split(":")
        hour = parts[0].zfill(2)
        minute = parts[1].zfill(2) if len(parts) > 1 else "00"
        return f"{hour}:{minute}"
    except Exception:
        return "00:00"


# ---------- SAVE ----------
def save_profile(bank, name, biz_type, location, audience, platforms):
    memory = get_memory_client()
    content = (f"Business profile: {name} is a {biz_type} located in {location}. "
               f"Target audience: {audience}. It posts on: {platforms}.")
    memory.retain(bank_id=bank, content=content, context="business profile")


def save_post(bank, date, time, platform, post_type, caption,
              likes, comments, shares, reach, reaction):
    memory = get_memory_client()
    content = (
        f"On {date} at {time}, {platform} {post_type} was posted. "
        f"Caption: \"{caption}\". "
        f"Results: {likes} likes, {comments} comments, {shares} shares, reach {reach}. "
        f"Audience reaction: {reaction}"
    )
    safe_time = _pad_time(time)
    memory.retain(bank_id=bank, content=content,
                  context="post performance and audience reaction",
                  timestamp=f"{date}T{safe_time}:00Z")
    _append_local(bank, dict(date=str(date), time=time, platform=platform,
                             post_type=post_type, caption=caption, likes=likes,
                             comments=comments, shares=shares, reach=reach,
                             reaction=reaction))


def save_event(bank, name, date, notes):
    memory = get_memory_client()
    content = f"Local event or festival: {name} on {date}. {notes}"
    memory.retain(bank_id=bank, content=content,
                  context="local festival or event", timestamp=f"{date}T09:00:00Z")


# ---------- RECALL ----------
def gather_memories(bank, queries):
    """Run several searches and merge the unique results, with retry on failure."""
    memory = get_memory_client()
    seen, out = set(), []
    for q in queries:
        success = False
        for attempt in range(3):
            try:
                res = memory.recall(bank_id=bank, query=q)
                print(f"[recall OK] bank={bank} query='{q}' -> {len(res.results)} results")
                for r in res.results:
                    if r.text not in seen:
                        seen.add(r.text)
                        out.append(r.text)
                success = True
                break
            except Exception as e:
                print(f"[recall FAIL attempt {attempt+1}] bank={bank} query='{q}' -> {e}")
                time.sleep(1.5)
        if not success:
            print(f"[recall GAVE UP] bank={bank} query='{q}'")
        time.sleep(0.3)
    return out


def reflect_insights(bank):
    memory = get_memory_client()
    res = memory.reflect(
        bank_id=bank,
        query=("Based on all past posts, what content types, posting times and "
               "topics work best for this audience, and what does not work? "
               "How do local festivals affect engagement?"),
    )
    return res.text


# ---------- LOCAL COPY (for charts/tables) ----------
def _path(bank):
    return os.path.join(DATA_DIR, f"{bank}.json")


def load_posts(bank):
    if os.path.exists(_path(bank)):
        with open(_path(bank), encoding="utf-8") as f:
            return json.load(f)
    return []


def _append_local(bank, row):
    rows = load_posts(bank)
    rows.append(row)
    with open(_path(bank), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
import os, re, json
from core import memory

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def bank_for(business_name):
    slug = re.sub(r"[^a-z0-9]+", "-", business_name.lower()).strip("-")
    return f"biz-{slug}"

# ---------- SAVE ----------
def save_profile(bank, name, biz_type, location, audience, platforms):
    content = (f"Business profile: {name} is a {biz_type} located in {location}. "
               f"Target audience: {audience}. It posts on: {platforms}.")
    memory.retain(bank_id=bank, content=content, context="business profile")

def save_post(bank, date, time, platform, post_type, caption,
              likes, comments, shares, reach, reaction):
    content = (
        f"On {date} at {time}, {platform} {post_type} was posted. "
        f"Caption: \"{caption}\". "
        f"Results: {likes} likes, {comments} comments, {shares} shares, reach {reach}. "
        f"Audience reaction: {reaction}"
    )
    memory.retain(bank_id=bank, content=content,
                  context="post performance and audience reaction",
                  timestamp=f"{date}T{time}:00Z")
    _append_local(bank, dict(date=str(date), time=time, platform=platform,
                             post_type=post_type, caption=caption, likes=likes,
                             comments=comments, shares=shares, reach=reach,
                             reaction=reaction))

def save_event(bank, name, date, notes):
    content = f"Local event or festival: {name} on {date}. {notes}"
    memory.retain(bank_id=bank, content=content,
                  context="local festival or event", timestamp=f"{date}T09:00:00Z")

# ---------- RECALL ----------
def gather_memories(bank, queries):
    """Run several searches and merge the unique results."""
    seen, out = set(), []
    for q in queries:
        try:
            res = memory.recall(bank_id=bank, query=q)
            for r in res.results:
                if r.text not in seen:
                    seen.add(r.text)
                    out.append(r.text)
        except Exception as e:
            print(f"[recall error] {e}")
    return out

def reflect_insights(bank):
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
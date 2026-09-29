import streamlit as st
import pandas as pd
from datetime import date
import memory_ops as mo
import agent

st.title("📣 LocalBuzz")
st.markdown("**Stop guessing what to post.** LocalBuzz remembers your posts, "
            "your customers' reactions and your neighbourhood's festivals, "
            "and tells you exactly what to post next.")

st.sidebar.header("Your business")
business = st.sidebar.text_input("Business name", "Sweet Crumbs Bakery")
bank = mo.bank_for(business)
st.sidebar.caption(f"Memory bank: `{bank}`")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**How it works**\n\n"
    "1. Log posts, reactions and local events\n"
    "2. Hindsight remembers everything per business\n"
    "3. The agent recalls your history and recommends what to post\n\n"
    "_Powered by Hindsight memory._"
)

tab_rec, tab_post, tab_event, tab_profile, tab_insights = st.tabs(
    ["💡 Recommendations", "📝 Log a post", "🎉 Log local event",
     "🏪 Business profile", "📊 Insights"])

# ---- Recommendations ----
with tab_rec:
    with st.spinner("Checking for patterns..."):
        nudge = agent.proactive_nudge(bank)
    if nudge:
        st.info(f"**LocalBuzz noticed:** {nudge}")

    request = st.text_input("What do you need?", "What should I post this week?")
    st.caption("Try: 'Plan for the next festival' · 'Why did my Sunday post flop?' · "
               "'What should I post about a new product?'")
    col_a, col_b = st.columns(2)
    go_rec = col_a.button("💡 Get recommendations", type="primary")
    go_plan = col_b.button("📅 Build my 7-day calendar")

    if go_rec:
        with st.spinner("Recalling your history and thinking..."):
            answer, mems, is_cold = agent.recommend(bank, request)
        if is_cold:
            st.warning(f"This business has only {len(mems)} memory item(s) so far. "
                       "Advice below is general — log some posts to get personalized recommendations.")
        else:
            st.success(f"Personalized using {len(mems)} memories from this business's history.")
        st.markdown(answer)
        with st.expander(f"🧠 Memories used ({len(mems)})"):
            for m in mems:
                st.write("•", m)

    if go_plan:
        with st.spinner("Planning your week from your history..."):
            answer, mems = agent.weekly_plan(bank)
        st.markdown(answer)
        with st.expander(f"🧠 Memories used ({len(mems)})"):
            for m in mems:
                st.write("•", m)

# ---- Log a post ----
with tab_post:
    with st.form("post_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Date posted", date.today())
        t = c2.text_input("Time (HH:MM, 24h)", "19:00")
        platform = c3.selectbox("Platform", ["Instagram", "Facebook", "WhatsApp Status", "Other"])
        ptype = st.selectbox("Post type", ["Reel", "Photo", "Carousel", "Story", "Story poll", "Text"])
        caption = st.text_area("Caption / what the post was about")
        c4, c5, c6, c7 = st.columns(4)
        likes = c4.number_input("Likes", 0, step=1)
        comments = c5.number_input("Comments", 0, step=1)
        shares = c6.number_input("Shares", 0, step=1)
        reach = c7.number_input("Reach", 0, step=1)
        reaction = st.text_area("What did people say or do? (comments, DMs, orders)")
        if st.form_submit_button("Save to memory"):
            try:
                mo.save_post(bank, str(d), t, platform, ptype, caption,
                             int(likes), int(comments), int(shares), int(reach), reaction)
                st.success("Saved! The agent will learn from this.")
            except Exception as e:
                st.error(f"Could not save: {e}")

# ---- Log event ----
with tab_event:
    with st.form("event_form", clear_on_submit=True):
        ename = st.text_input("Event / festival name", "")
        edate = st.date_input("Event date", date.today())
        enotes = st.text_area("Notes (e.g. what sold well last time, local footfall)")
        if st.form_submit_button("Save event"):
            try:
                mo.save_event(bank, ename, str(edate), enotes)
                st.success("Event saved.")
            except Exception as e:
                st.error(f"Could not save: {e}")

# ---- Profile ----
with tab_profile:
    with st.form("profile_form"):
        btype = st.text_input("Type of business", "neighbourhood bakery")
        loc = st.text_input("Neighbourhood / city", "Pune")
        aud = st.text_area("Your audience", "young families and college students")
        plats = st.text_input("Platforms you use", "Instagram, Facebook")
        if st.form_submit_button("Save profile"):
            try:
                mo.save_profile(bank, business, btype, loc, aud, plats)
                st.success("Profile saved.")
            except Exception as e:
                st.error(f"Could not save: {e}")

# ---- Insights ----
with tab_insights:
    posts = mo.load_posts(bank)
    if posts:
        df = pd.DataFrame(posts)
        st.subheader("Average engagement by post type")
        st.bar_chart(df.groupby("post_type")[["likes", "comments", "shares"]].mean())
        st.subheader("Post history")
        st.dataframe(df[["date", "time", "platform", "post_type", "caption",
                         "likes", "comments", "shares", "reach"]], use_container_width=True)
    else:
        st.info("No posts logged yet.")
    if st.button("🧠 Ask Hindsight what it has learned"):
        with st.spinner("Reflecting on memories..."):
            try:
                st.markdown(mo.reflect_insights(bank))
            except Exception as e:
                st.error(f"Reflect failed: {e}")
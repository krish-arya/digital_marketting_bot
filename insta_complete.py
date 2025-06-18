import streamlit as st
import requests
from urllib.parse import quote
from datetime import datetime
import streamlit.components.v1 as components

# ========== CONFIG ==========
st.set_page_config(page_title="Instagram Reels Viewer", page_icon="🎞️", layout="wide")
st.title("🎞️ Instagram Profile & Reels Viewer")

API_KEY = ""
DEFAULT_REEL_COUNT = 10

# ========== INPUT ==========
handle = st.text_input("Enter Instagram handle (without @):")

# ========== HELPERS ==========
def fetch_profile(handle):
    url = f"https://api.scrapecreators.com/v1/instagram/profile?handle={quote(handle)}"
    headers = {"x-api-key": API_KEY}
    try:
        res = requests.get(url, headers=headers)
        return res.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_reels(handle, amount=DEFAULT_REEL_COUNT):
    url = f"https://api.scrapecreators.com/v1/instagram/user/reels/simple?handle={quote(handle)}&amount={amount}"
    headers = {"x-api-key": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def format_number(num):
    if not num:
        return "NA"
    num = int(num)
    return f"{num/1_000_000:.1f}M" if num >= 1_000_000 else f"{num/1_000:.1f}K" if num >= 1000 else str(num)

def format_timestamp(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%B %d, %Y at %I:%M %p")
    except:
        return "Unknown"

if handle:
    with st.spinner("Fetching profile and reels..."):
        profile = fetch_profile(handle)
        reels_data = fetch_reels(handle)

    if profile.get("success") and "data" in profile:
        user = profile["data"]["user"]
        st.markdown(f"""
        <div style='display: flex; gap: 20px; align-items: center; margin-bottom: 30px;'>
            <img src="{user.get("profile_pic_url_hd")}" style='width: 90px; height: 90px; border-radius: 50%; border: 2px solid #ccc;'>
            <div>
                <h2 style='margin: 0;'>{user.get("full_name", "Unknown")}</h2>
                <p style='margin: 0; font-size: 16px;'>@{user.get("username")}</p>
                <p style='margin: 5px 0;'>{user.get("biography", "No bio available.")}</p>
                <p>👥 <b>Followers:</b> {format_number(user.get("edge_followed_by", {}).get("count"))} | <b>Following:</b> {format_number(user.get("edge_follow", {}).get("count"))}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if user.get("bio_links"):
            st.subheader("🔗 Bio Links")
            for link in user["bio_links"]:
                st.markdown(f"- [{link['title'] or link['url']}]({link['url']})")

    else:
        st.error("❌ Couldn't fetch profile information.")
        st.write(profile)

    if isinstance(reels_data, list) and reels_data:
        st.subheader("🎥 Latest Reels")
        for media_data in reels_data:
            media = media_data.get("media")
            if not media:
                continue

            caption = media.get("caption", {}).get("text") if isinstance(media.get("caption"), dict) else media.get("caption", "No caption")
            taken_at = format_timestamp(media.get("taken_at", 0))
            play_count = format_number(media.get("play_count") or media.get("ig_play_count"))
            like_count = format_number(media.get("like_count"))
            share_count = format_number(media.get("share_count"))
            video_url = f"https://www.instagram.com/reel/{media.get('code', '')}/"
            thumbnail = media.get("display_uri")

            html = f"""
            <div style='background: #fff; border-radius: 20px; padding: 20px; margin-bottom: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);'>
                <img src="{thumbnail}" style="width: 100%; border-radius: 12px; margin-bottom: 10px;" />
                <p><strong>📝 Caption:</strong> {caption}</p>
                <p><strong>📅 Uploaded:</strong> {taken_at}</p>
                <p><strong>▶️ Plays:</strong> {play_count} | ❤️ Likes: {like_count} | 🔁 Shares: {share_count or 'NA'}</p>
                <p><a href='{video_url}' target='_blank'>🔗 View Reel</a></p>
            </div>
            """
            components.html(html, height=400)
    else:
        st.warning("No reels found or failed to load reels.")
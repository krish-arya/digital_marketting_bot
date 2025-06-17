import streamlit as st
import requests
from urllib.parse import quote
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Instagram Reels Viewer", page_icon="🎞️", layout="wide")
st.title("🎞️ Instagram Reels Visualizer")

st.markdown("Enter an Instagram username to view recent reels beautifully formatted.")

handle = st.text_input("Instagram handle (without @)")

API_KEY = ""
DEFAULT_REEL_COUNT = 17

def fetch_reels(handle, amount=DEFAULT_REEL_COUNT):
    url = f"https://api.scrapecreators.com/v1/instagram/user/reels/simple?handle={quote(handle)}&amount={amount}"
    headers = {"x-api-key": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"Status Code: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def format_number(num):
    if num is None:
        return "NA"
    try:
        num = int(num)
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    except:
        return "NA"

def format_timestamp(timestamp):
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return "Unknown"

if handle:
    with st.spinner("Fetching reels..."):
        response_data = fetch_reels(handle)

    if isinstance(response_data, list):
        reels = [item.get("media") for item in response_data if "media" in item]
    else:
        st.error("❌ Failed to fetch reels or unexpected response format.")
        st.write(response_data)
        reels = []

    if reels:
        user = reels[0].get("user", {})
        username = user.get("username", "unknown")
        fullname = user.get("full_name", "Unknown")
        profile_pic = user.get("profile_pic_url", "")

        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 20px; margin-top: 10px; margin-bottom: 30px;'>
            <img src="{profile_pic}" style='border-radius: 50%; width: 80px; height: 80px; border: 2px solid #ccc;'>
            <div>
                <h3 style='margin: 0;'>{fullname}</h3>
                <p style='margin: 0; font-size: 16px;'>@{username}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for media in reels:
            caption = media.get("caption", {})
            caption_text = caption.get("text") if isinstance(caption, dict) else caption or "No caption"
            taken_at = format_timestamp(media.get("taken_at", 0))
            play_count = format_number(media.get("play_count") or media.get("ig_play_count"))
            like_count = format_number(media.get("like_count"))
            share_count = format_number(media.get("share_count"))
            video_url = f"https://www.instagram.com/reel/{media.get('code', '')}/"

            thumbnail = media.get("display_uri")
            if not thumbnail:
                candidates = media.get("image_versions2", {}).get("candidates", [])
                thumbnail = candidates[0].get("url", "") if candidates else ""

            html = f"""
            <div style='background: #fff; border-radius: 20px; padding: 20px; margin-bottom: 20px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1); font-family: sans-serif;'>
                <div style='margin-bottom: 10px;'>
                    <a href='{video_url}' target='_blank'>
                        <img src='{thumbnail}' style='width: 100%; max-height: 200px; object-fit: cover; border-radius: 15px;' onerror="this.style.display='none'">
                    </a>
                </div>
                <p><strong>📝 Caption:</strong> {caption_text}</p>
                <p><strong>📅 Uploaded:</strong> {taken_at}</p>
                <p><strong>▶️ Plays:</strong> {play_count} | ❤️ Likes: {like_count} | 🔁 Shares: {share_count or 'NA'}</p>
                <p><a href='{video_url}' target='_blank'>🔗 View Reel</a></p>
            </div>
            """
            components.html(html, height=200, scrolling=False)
    else:
        st.warning("No reels found.")

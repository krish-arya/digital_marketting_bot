import streamlit as st
import requests
import io
from PIL import Image
from datetime import datetime
from urllib.parse import quote
import streamlit.components.v1 as components
from streamlit_carousel import carousel

API_KEY = ""

st.set_page_config(page_title="Unified Ads Explorer", page_icon="📊", layout="wide")
st.title("📊 Unified Ads Intelligence Dashboard")

# Tab selection
tab = st.sidebar.radio("Choose Platform", ["Facebook Ads", "Google Ads", "Instagram Viewer"])

# ------------------ FACEBOOK ADS ------------------
if tab == "Facebook Ads":
    st.header("📘 Facebook Ads Explorer")

    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    if 'page_id' not in st.session_state:
        st.session_state.page_id = ""
    if 'ads_data' not in st.session_state:
        st.session_state.ads_data = None
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None

    def fetch_company_data(query):
        url = f"https://api.scrapecreators.com/v1/facebook/adLibrary/search/companies?query={quote(query)}"
        res = requests.get(url, headers={"x-api-key": API_KEY})
        return res.json() if res.status_code == 200 else None

    def fetch_ads_data(page_id):
        url = f"https://api.scrapecreators.com/v1/facebook/adLibrary/company/ads?pageId={page_id}"
        res = requests.get(url, headers={"x-api-key": API_KEY})
        return res.json() if res.status_code == 200 else None

    def format_date(date_str):
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime("%b %d, %Y")
        except:
            return "N/A"

    def display_ad_card(ad, index):
        st.markdown("---")
        st.subheader(f"Ad {index+1}")
        st.write(f"**Start Date:** {format_date(ad.get('start_date_string'))}")
        st.write(f"**Ad ID:** {ad.get('ad_archive_id', 'N/A')}")
        snapshot = ad.get("snapshot", {})
        st.write(f"**Page Name:** {snapshot.get('page_name', 'N/A')}")
        st.write(f"**Ad Text:** {snapshot.get('body', {}).get('text', 'No ad body available.')}")
        if snapshot.get("cta_text"):
            st.write(f"**CTA:** {snapshot.get('cta_text')}")
        if snapshot.get("caption"):
            st.write(f"**Caption:** {snapshot.get('caption')}")
        if snapshot.get("title"):
            st.write(f"**Title:** {snapshot.get('title')}")
        if snapshot.get("link_url"):
            st.markdown(f"[🔗 Link]({snapshot.get('link_url')})")

    fb_mode = st.radio("Choose Method", ["Search Company", "Enter Page ID"])

    if fb_mode == "Search Company":
        query = st.text_input("Search for a company")
        if st.button("Search") and query:
            st.session_state.search_results = fetch_company_data(query)

        if st.session_state.search_results:
            for i, comp in enumerate(st.session_state.search_results.get("searchResults", [])):
                with st.expander(comp.get("name", "N/A")):
                    st.write(f"Category: {comp.get('category')}")
                    st.write(f"Page ID: {comp.get('page_id')}")
                    if st.button("Select", key=f"select_{i}"):
                        st.session_state.page_id = comp["page_id"]
                        st.rerun()
    else:
        st.session_state.page_id = st.text_input("Enter Facebook Page ID")

    if st.session_state.page_id:
        ads_data = fetch_ads_data(st.session_state.page_id)
        if ads_data and "results" in ads_data:
            for i, ad in enumerate(ads_data["results"]):
                display_ad_card(ad, i)


# ------------------ GOOGLE ADS ------------------
elif tab == "Google Ads":
    st.header("🔍 Google Ads Viewer")

    def fetch_google_ads(domain):
        url = f"https://api.scrapecreators.com/v1/google/company/ads?domain={domain}"
        headers = {"x-api-key": API_KEY}
        res = requests.get(url, headers=headers)
        return res.json().get("ads", []) if res.status_code == 200 else []

    domain = st.text_input("Enter company domain (e.g., hazoorilallegacy.com)")

    if domain.strip():
        ads = fetch_google_ads(domain)
        for i, ad in enumerate(ads):
            st.markdown("---")
            st.markdown(f"### Ad {i+1}")
            st.write(f"**First Shown:** {datetime.fromisoformat(ad['firstShown'].replace('Z','+00:00')).strftime('%b %d, %Y %H:%M')}")
            st.write(f"**Last Shown:** {datetime.fromisoformat(ad['lastShown'].replace('Z','+00:00')).strftime('%b %d, %Y %H:%M')}")
            st.write(f"**Format:** {ad.get('format', 'N/A')}")
            st.write(f"**Advertiser ID:** {ad.get('advertiserId', 'N/A')}")
            st.write(f"**Creative ID:** {ad.get('creativeId', 'N/A')}")
            st.markdown(f"[🔗 View Ad]({ad['adUrl']})")

# ------------------ INSTAGRAM ------------------
elif tab == "Instagram Viewer":
    st.header("🎞️ Instagram Reels Viewer")
    DEFAULT_REEL_COUNT = 10

    def fetch_profile(handle):
        url = f"https://api.scrapecreators.com/v1/instagram/profile?handle={quote(handle)}"
        headers = {"x-api-key": API_KEY}
        return requests.get(url, headers=headers).json()

    def fetch_reels(handle, amount=DEFAULT_REEL_COUNT):
        url = f"https://api.scrapecreators.com/v1/instagram/user/reels/simple?handle={quote(handle)}&amount={amount}"
        headers = {"x-api-key": API_KEY}
        return requests.get(url, headers=headers).json()

    def format_number(n):
        return f"{int(n)/1_000_000:.1f}M" if int(n) >= 1_000_000 else f"{int(n)/1_000:.1f}K" if int(n) >= 1_000 else str(n)

    def format_timestamp(ts):
        try:
            return datetime.fromtimestamp(int(ts)).strftime("%B %d, %Y at %I:%M %p")
        except:
            return "Unknown"

    handle = st.text_input("Enter Instagram Handle (without @)")

    if handle:
        profile = fetch_profile(handle)
        reels_data = fetch_reels(handle)

        if profile.get("success") and "data" in profile:
            user = profile["data"]["user"]
            st.markdown(f"""
            <div style='display: flex; gap: 20px; align-items: center;'>
                <img src="{user.get('profile_pic_url_hd')}" style='width: 90px; height: 90px; border-radius: 50%; border: 2px solid #ccc;'>
                <div>
                    <h2 style='margin: 0;'>{user.get('full_name')}</h2>
                    <p>@{user.get('username')}</p>
                    <p>{user.get('biography')}</p>
                    <p>👥 Followers: {format_number(user.get('edge_followed_by', {}).get('count'))} | Following: {format_number(user.get('edge_follow', {}).get('count'))}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if isinstance(reels_data, list):
            st.subheader("🎥 Latest Reels")
            for media_data in reels_data:
                media = media_data.get("media", {})
                caption = media.get("caption", {}).get("text") if isinstance(media.get("caption"), dict) else media.get("caption")
                taken_at = format_timestamp(media.get("taken_at", 0))
                play_count = format_number(media.get("play_count") or media.get("ig_play_count", 0))
                like_count = format_number(media.get("like_count", 0))
                share_count = format_number(media.get("share_count", 0))
                video_url = f"https://www.instagram.com/reel/{media.get('code', '')}/"
                thumb = media.get("display_uri")

                html = f"""
                <div style='background: #fff; padding: 20px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 30px;'>
                    <img src="{thumb}" style='width: 100%; border-radius: 12px;'>
                    <p><b>📝 Caption:</b> {caption}</p>
                    <p><b>📅 Uploaded:</b> {taken_at}</p>
                    <p><b>▶️ Plays:</b> {play_count} | ❤️ Likes: {like_count} | 🔁 Shares: {share_count}</p>
                    <p><a href='{video_url}' target='_blank'>🔗 View Reel</a></p>
                </div>
                """
                components.html(html, height=400)
        else:
            st.warning("No reels found or failed to load reels.")
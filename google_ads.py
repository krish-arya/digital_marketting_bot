import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(page_title="Google Ads Viewer", layout="wide")
st.title("Google Ads Viewer")

API_KEY = ""

# Input for domain
domain = st.text_input("Enter a company domain (e.g., www.nike.com)")

@st.cache_data(show_spinner=False)
def fetch_google_ads(domain):
    try:
        url = f"https://api.scrapecreators.com/v1/google/company/ads?domain={domain}"
        headers = {"x-api-key": API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("ads", [])
        else:
            st.error(f"Failed with status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

if domain.strip():
    ads = fetch_google_ads(domain)
    if ads:
        st.subheader(f"Found {len(ads)} ads for {domain}")

        for i, ad in enumerate(ads):
            st.markdown("---")
            st.markdown(f"### Ad {i+1}")
            st.write(f"**First Shown:** {datetime.fromisoformat(ad['firstShown'].replace('Z','+00:00')).strftime('%b %d, %Y %H:%M')}")
            st.write(f"**Last Shown:** {datetime.fromisoformat(ad['lastShown'].replace('Z','+00:00')).strftime('%b %d, %Y %H:%M')}")
            st.write(f"**Format:** {ad.get('format', 'N/A').capitalize()}")
            st.write(f"**Advertiser ID:** {ad.get('advertiserId', 'N/A')}")
            st.write(f"**Creative ID:** {ad.get('creativeId', 'N/A')}")
            st.markdown(f"[🔗 View Ad]({ad['adUrl']})")
    else:
        st.info("No ads found for this domain.")

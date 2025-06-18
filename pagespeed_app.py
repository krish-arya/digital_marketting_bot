import streamlit as st
import requests
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="PageSpeed Score", page_icon="🚀", layout="centered")
st.title("🚀 Google PageSpeed Insights Checker")

# --- API KEY ---
API_KEY = ""  # Replace with your own API key if needed

# --- Input Fields ---
url = st.text_input("Enter full website URL (include https://):", "https://web.dev/")
strategy = st.radio("Choose device type:", ["mobile", "desktop"])

# --- On Button Click ---
if st.button("Run Analysis"):
    st.info("Fetching performance data...")

    api_url = (
        f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={url}&strategy={strategy}&key={API_KEY}"
    )

    try:
        response = requests.get(api_url)
        data = response.json()

        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        # --- Lighthouse Performance Score Only ---
        st.subheader("📊 Lighthouse Category Score")
        performance_score = categories.get("performance", {}).get("score")
        if performance_score is not None:
            st.metric("🚀 Performance", f"{int(performance_score * 100)} / 100")
        else:
            st.warning("Performance score not available.")

        st.divider()

        # --- Core Web Vitals ---
        st.subheader("⚡ Core Web Vitals")
        col1, col2 = st.columns(2)

        def safe_metric(label, key, col):
            val = audits.get(key, {}).get("displayValue", "N/A")
            col.metric(label, val)

        safe_metric("Speed Index", "speed-index", col1)
        safe_metric("First Contentful Paint", "first-contentful-paint", col1)
        safe_metric("Largest Contentful Paint", "largest-contentful-paint", col1)

        safe_metric("Time to Interactive", "interactive", col2)
        safe_metric("Total Blocking Time", "total-blocking-time", col2)
        safe_metric("Cumulative Layout Shift", "cumulative-layout-shift", col2)

        st.divider()

        # --- Additional Diagnostics ---
        st.subheader("🛠 Additional Diagnostics")
        diagnostic_keys = [
            "uses-long-cache-ttl", "uses-optimized-images", "dom-size",
            "render-blocking-resources", "bootup-time", "main-thread-tasks",
            "unminified-css", "unminified-javascript", "uses-text-compression",
            "uses-responsive-images", "uses-webp-images"
        ]

        for key in diagnostic_keys:
            item = audits.get(key, {})
            if item and item.get("scoreDisplayMode") != "notApplicable":
                st.write(f"**{item.get('title', key)}** — {item.get('displayValue', 'N/A')}")

        st.divider()

        # --- Timestamp ---
        if lighthouse.get("fetchTime"):
            ts = datetime.strptime(lighthouse["fetchTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            st.markdown(f"📅 **Analysis Timestamp:** {ts.strftime('%b %d, %Y %I:%M %p')}")

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")

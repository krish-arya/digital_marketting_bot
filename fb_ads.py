import streamlit as st
import requests
from PIL import Image
import io
import datetime
from urllib.parse import quote

# Set page config
st.set_page_config(
    page_title="Facebook Ads Explorer",
    page_icon="📊",
    layout="wide"
)

# API key
API_KEY = ""

# Initialize session state
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'page_id' not in st.session_state:
    st.session_state.page_id = ""
if 'ads_data' not in st.session_state:
    st.session_state.ads_data = None
if 'current_search_query' not in st.session_state:
    st.session_state.current_search_query = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

# Functions
def fetch_company_data(query):
    try:
        encoded_query = quote(query)
        url = f"https://api.scrapecreators.com/v1/facebook/adLibrary/search/companies?query={encoded_query}"
        response = requests.get(url, headers={"x-api-key": API_KEY})
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def fetch_ads_data(page_id):
    try:
        url = f"https://api.scrapecreators.com/v1/facebook/adLibrary/company/ads?pageId={page_id}"
        response = requests.get(url, headers={"x-api-key": API_KEY})
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

def display_media(media_url, media_type="image"):
    """Display image or video based on media type"""
    if not media_url:
        st.write("No media available")
        return
    
    try:
        if media_type == "video" or any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm']):
            st.video(media_url)
        else:
            # Try to load as image
            response = requests.get(media_url, timeout=10)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, use_container_width=True)
            else:
                st.write("Media not available")
    except Exception as e:
        st.write(f"Could not load media: {str(e)}")

def display_ad_card(ad, index):
    """Display individual ad card"""
    with st.container():
        st.markdown("---")
        
        # Ad header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Ad {index + 1}")
        with col2:
            status = "🟢 Active" if ad.get("is_active") else "🔴 Inactive"
            st.write(status)
        
        # Ad details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Start Date:** {format_date(ad.get('start_date_string'))}")
        with col2:
            st.write(f"**Ad ID:** {ad.get('ad_archive_id', 'N/A')}")
        with col3:
            if ad.get("impressions"):
                min_imp = ad["impressions"].get("lower_bound", "N/A")
                max_imp = ad["impressions"].get("upper_bound", "N/A")
                st.write(f"**Impressions:** {min_imp}-{max_imp}")
        
        # Ad content
        snapshot = ad.get("snapshot", {})
        cards = snapshot.get("cards", [])
        
        if cards:
            card = cards[0]  # Show first card
            
            # Title and body
            if card.get("title"):
                st.write(f"**Title:** {card.get('title')}")
            
            if card.get("body"):
                st.write(f"**Description:** {card.get('body')}")
            
            # Display media (images and videos)
            col1, col2 = st.columns(2)
            
            with col1:
                # Original image
                if card.get("original_image_url"):
                    st.write("**Image:**")
                    display_media(card["original_image_url"], "image")
            
            with col2:
                # Video (if available)
                if card.get("video_url"):
                    st.write("**Video:**")
                    display_media(card["video_url"], "video")
                elif card.get("video_hd_url"):
                    st.write("**Video (HD):**")
                    display_media(card["video_hd_url"], "video")
                elif card.get("video_sd_url"):
                    st.write("**Video (SD):**")
                    display_media(card["video_sd_url"], "video")
            
            # Call to action
            if card.get("cta_text"):
                st.write(f"**Call to Action:** {card.get('cta_text')}")
            
            # Link preview (if available)
            if card.get("link_caption"):
                st.write(f"**Link Caption:** {card.get('link_caption')}")
            if card.get("link_description"):
                st.write(f"**Link Description:** {card.get('link_description')}")
        
        # Footer info
        col1, col2 = st.columns(2)
        with col1:
            platforms = ad.get("publisher_platform", [])
            if platforms:
                st.write(f"**Platforms:** {', '.join(platforms)}")
        with col2:
            if ad.get("url"):
                st.write(f"[View Original Ad]({ad['url']})")

# App header
st.title("📊 Facebook Ads Explorer")
st.write("Discover companies and analyze their Facebook ad campaigns")

# Tab selection
tab = st.radio(
    "Select Mode:",
    ["🔍 Search Companies", "📝 Enter Page ID"],
    horizontal=True
)

if tab == "🔍 Search Companies":
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input("Search for a company", placeholder="Enter company name (e.g. Nike)")
        with col2:
            st.write("")
            submit_button = st.form_submit_button("🔍 Search")
    
    if submit_button and query:
        st.session_state.current_search_query = query
        with st.spinner("Searching for companies..."):
            data = fetch_company_data(query)
            st.session_state.search_results = data
    
    # Display search results
    if st.session_state.search_results and "searchResults" in st.session_state.search_results:
        results = st.session_state.search_results["searchResults"]
        st.write(f"Found {len(results)} results for '{st.session_state.current_search_query}'")
        
        for i, company in enumerate(results):
            with st.expander(f"{company.get('name', 'N/A')} - {company.get('category', 'N/A')}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Company image
                    if company.get("image_uri"):
                        try:
                            image = Image.open(io.BytesIO(requests.get(company["image_uri"]).content))
                            st.image(image, width=100)
                        except:
                            st.write("No image")
                    else:
                        st.write("No image")
                
                with col2:
                    # Company details
                    verification = "✅ Verified" if company.get("verification") == "VERIFIED" else "❌ Not Verified"
                    st.write(f"**Verification:** {verification}")
                    st.write(f"**Category:** {company.get('category', 'N/A')}")
                    st.write(f"**Type:** {company.get('entity_type', 'N/A').replace('_', ' ').title()}")
                    
                    # Handle likes safely
                    likes = company.get('likes')
                    if likes is not None:
                        st.write(f"**Likes:** {likes:,}")
                    else:
                        st.write("**Likes:** N/A")
                    
                    # Handle Instagram followers safely
                    ig_followers = company.get("ig_followers")
                    if ig_followers is not None:
                        st.write(f"**Instagram Followers:** {ig_followers:,}")
                    
                    if company.get("page_alias"):
                        st.write(f"**Page:** fb.com/{company.get('page_alias')}")
                    
                    st.write(f"**Page ID:** {company.get('page_id', 'N/A')}")
                
                if st.button(f"Select {company.get('name', 'Company')}", key=f"select_{i}"):
                    st.session_state.selected_company = company
                    st.session_state.page_id = company["page_id"]
                    st.session_state.ads_data = None
                    st.rerun()

else:  # Enter Page ID tab
    with st.form("page_id_form"):
        page_id = st.text_input("Enter Facebook Page ID", placeholder="e.g. 51212153078")
        submit_page_id = st.form_submit_button("🚀 Fetch Ads")
    
    if submit_page_id and page_id:
        st.session_state.page_id = page_id
        st.session_state.selected_company = None
        st.session_state.ads_data = None

# Display ads section
if st.session_state.page_id:
    st.markdown("---")
    st.header(f"📊 Ads for Page ID: {st.session_state.page_id}")
    
    # Show selected company info if available
    if st.session_state.selected_company:
        company = st.session_state.selected_company
        col1, col2 = st.columns([1, 4])
        with col1:
            if company.get("image_uri"):
                try:
                    image = Image.open(io.BytesIO(requests.get(company["image_uri"]).content))
                    st.image(image, width=100)
                except:
                    pass
        with col2:
            st.subheader(company.get("name", "N/A"))
            likes = company.get('likes')
            likes_text = f"{likes:,}" if likes is not None else "N/A"
            st.write(f"{company.get('category', 'N/A')} • {likes_text} likes")
    
    # Fetch and display ads
    if st.session_state.ads_data is None:
        with st.spinner(f"Fetching ads for Page ID: {st.session_state.page_id}..."):
            ads_data = fetch_ads_data(st.session_state.page_id)
            st.session_state.ads_data = ads_data
    
    if st.session_state.ads_data and "results" in st.session_state.ads_data:
        ads = st.session_state.ads_data["results"]
        
        if ads:
            # Summary stats
            active_ads = sum(1 for ad in ads if ad.get("is_active"))
            platforms = set()
            for ad in ads:
                platforms.update(ad.get("publisher_platform", []))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Ads", len(ads))
            with col2:
                st.metric("Active Ads", active_ads)
            with col3:
                st.write(f"**Platforms:** {', '.join(platforms) if platforms else 'N/A'}")
            
            # Display ads
            for i, ad in enumerate(ads):
                display_ad_card(ad, i)
        else:
            st.write("No ads found for this Page ID")
    elif st.session_state.page_id:
        st.error("Could not fetch ads data. Please check the Page ID and try again.")
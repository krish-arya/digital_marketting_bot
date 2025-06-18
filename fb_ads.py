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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        :root {
            --primary: #1877F2;
            --secondary: #42B72A;
            --dark: #1C1E21;
            --light: #FFFFFF;
            --gray: #4B4F56;
            --card-bg: #FFFFFF;
            --background: #F0F2F5;
        }
        body, .stApp {
            background-color: var(--background) !important;
            color: var(--dark) !important;
        }
        .header {
            font-size: 36px !important;
            font-weight: bold !important;
            color: var(--primary) !important;
            text-align: center;
            margin-bottom: 10px;
        }
        .subheader {
            font-size: 18px !important;
            color: var(--gray) !important;
            text-align: center;
            margin-bottom: 30px;
        }
        .search-box {
            max-width: 600px;
            margin: 0 auto 30px;
        }
        .result-count {
            color: var(--gray);
            margin-bottom: 20px;
            text-align: center;
        }
        .empty-state {
            text-align: center;
            padding: 50px;
            color: var(--gray);
        }
        
        /* Company Cards */
        .company-card {
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.05);
            background: var(--card-bg);
            border-left: 5px solid var(--primary);
        }
        .company-card.selected {
            border-left: 5px solid var(--secondary);
            background-color: #E7F3FF;
        }
        .company-name {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .company-category {
            font-size: 14px;
            color: var(--gray);
            margin-bottom: 10px;
        }
        .company-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        .stat-item {
            text-align: center;
            padding: 5px 10px;
            background: #F0F2F5;
            border-radius: 5px;
            font-size: 13px;
        }
        .verified-badge {
            background: var(--primary);
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 12px;
            display: inline-block;
            margin-left: 10px;
        }
        .not-verified {
            background: #E4E6EB;
            color: var(--gray);
        }
        
        /* Ads Grid */
        .ads-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        .ad-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-left: 4px solid var(--primary);
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .ad-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .ad-id {
            font-weight: bold;
            color: var(--primary);
            font-size: 16px;
        }
        .ad-status {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-active {
            background: var(--secondary);
            color: white;
        }
        .status-inactive {
            background: #65676B;
            color: white;
        }
        .ad-details {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }
        .detail-badge {
            background: #F0F2F5;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
        }
        .ad-content {
            flex-grow: 1;
            margin-bottom: 15px;
        }
        .ad-title {
            font-weight: bold;
            margin-bottom: 8px;
        }
        .ad-body {
            color: var(--gray);
            margin-bottom: 12px;
            line-height: 1.4;
        }
        .ad-image-container {
            margin: 12px 0;
            border-radius: 8px;
            overflow: hidden;
            background: #F7F8FA;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 200px;
        }
        .ad-image-container img {
            max-width: 100%;
            max-height: 300px;
            object-fit: contain;
        }
        .ad-cta {
            background: var(--primary);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            display: inline-block;
            margin-top: 10px;
            text-decoration: none;
        }
        .ad-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
            padding-top: 15px;
            border-top: 1px solid #EBEDF0;
        }
        .platform-tag {
            background: #E7F3FF;
            color: #1877F5;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
        }
        .view-link {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }
        
        /* Tabs */
        .tabs {
            background-color: white;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #E4E6EB;
        }
        .pill {
            background: #E7F3FF;
            color: var(--primary);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            display: inline-block;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        .stButton>button {
            background-color: var(--primary) !important;
            color: white !important;
            border: none;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# API key
API_KEY = ""

# App header
st.markdown('<p class="header">Facebook Ads Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Discover companies and analyze their Facebook ad campaigns</p>', unsafe_allow_html=True)

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

def display_ad_card(ad, index):
    with st.container():
        st.markdown(f'<div class="ad-card">', unsafe_allow_html=True)
        
        # Header
        st.markdown('<div class="ad-header">', unsafe_allow_html=True)
        st.markdown(f'<div class="ad-id">Ad {index+1}</div>', unsafe_allow_html=True)
        active_status = "Active" if ad.get("is_active") else "Inactive"
        status_class = "status-active" if ad.get("is_active") else "status-inactive"
        st.markdown(f'<div class="ad-status {status_class}">{active_status}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Details
        st.markdown('<div class="ad-details">', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-badge">📅 {format_date(ad.get("start_date_string"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-badge">🆔 {ad.get("ad_archive_id", "N/A")}</div>', unsafe_allow_html=True)
        
        if ad.get("impressions"):
            min_imp = ad["impressions"].get("lower_bound", "N/A")
            max_imp = ad["impressions"].get("upper_bound", "N/A")
            st.markdown(f'<div class="detail-badge">👀 {min_imp}-{max_imp}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content
        snapshot = ad.get("snapshot", {})
        cards = snapshot.get("cards", [])
        
        if cards:
            card = cards[0]  # Only show first card
            st.markdown('<div class="ad-content">', unsafe_allow_html=True)
            
            if card.get("title"):
                st.markdown(f'<div class="ad-title">{card.get("title")}</div>', unsafe_allow_html=True)
            
            if card.get("body"):
                st.markdown(f'<div class="ad-body">{card.get("body")}</div>', unsafe_allow_html=True)
            
            if card.get("original_image_url"):
                st.markdown('<div class="ad-image-container">', unsafe_allow_html=True)
                try:
                    image = Image.open(io.BytesIO(requests.get(card["original_image_url"]).content))
                    st.image(image, use_column_width=True)
                except:
                    st.markdown('<div style="color:#65676B;">Image not available</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if card.get("cta_text"):
                st.markdown(f'<a href="#" class="ad-cta">{card.get("cta_text")}</a>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown('<div class="ad-footer">', unsafe_allow_html=True)
        platforms = ad.get("publisher_platform", [])
        if platforms:
            st.markdown(f'<div class="platform-tag">{platforms[0]}</div>', unsafe_allow_html=True)
        if ad.get("url"):
            st.markdown(f'<a href="{ad["url"]}" target="_blank" class="view-link">View Ad</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Tab selection
st.markdown('<div class="tabs">', unsafe_allow_html=True)
tab = st.radio(
    "Select Mode:",
    ["🔍 Search Companies", "📝 Enter Page ID"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

if tab == "🔍 Search Companies":
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input("Search for a company", 
                                placeholder="Enter company name (e.g. Nike)", 
                                key="search_input_widget")
        with col2:
            st.write("")
            submit_button = st.form_submit_button("🔍 Search")
    
    if submit_button:
        query = st.session_state.search_input_widget
        if query:
            st.session_state.current_search_query = query
            with st.spinner("Searching for companies..."):
                data = fetch_company_data(query)
                st.session_state.search_results = data
    
    # Display results
    if st.session_state.search_results:
        data = st.session_state.search_results
        if "searchResults" in data:
            results = data["searchResults"]
            st.markdown(f'<p class="result-count">Found {len(results)} results for "{st.session_state.current_search_query}"</p>', unsafe_allow_html=True)
            
            for company in results:
                is_selected = st.session_state.selected_company and st.session_state.selected_company["page_id"] == company["page_id"]
                card_class = "company-card selected" if is_selected else "company-card"
                
                with st.container():
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if company.get("image_uri"):
                            try:
                                image = Image.open(io.BytesIO(requests.get(company["image_uri"]).content))
                                st.image(image, width=80)
                            except:
                                st.image("https://via.placeholder.com/80?text=No+Image", width=80)
                        else:
                            st.image("https://via.placeholder.com/80?text=No+Image", width=80)
                    
                    with col2:
                        verification_status = company.get("verification", "NOT_VERIFIED")
                        verification_class = "verified-badge" if verification_status == "VERIFIED" else "verified-badge not-verified"
                        verification_text = "Verified" if verification_status == "VERIFIED" else "Not Verified"
                        
                        st.markdown(f"""
                            <div class="company-name">
                                {company.get("name", "N/A")}
                                <span class="{verification_class}">{verification_text}</span>
                            </div>
                            <div class="company-category">
                                {company.get("category", "N/A")} • {company.get("entity_type", "N/A").replace("_", " ").title()}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="company-stats">', unsafe_allow_html=True)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f'<div class="stat-item">👍 {company.get("likes", 0)} Likes</div>', unsafe_allow_html=True)
                    with col2:
                        ig_followers = company.get("ig_followers")
                        if ig_followers is not None:
                            st.markdown(f'<div class="stat-item">📷 {ig_followers} IG Followers</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="stat-item">📷 No IG Data</div>', unsafe_allow_html=True)
                    with col3:
                        page_alias = company.get("page_alias")
                        if page_alias:
                            st.markdown(f'<div class="stat-item">🔗 fb.com/{page_alias}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="stat-item">🔗 No Page Alias</div>', unsafe_allow_html=True)
                    with col4:
                        st.markdown(f'<div class="stat-item">🆔 {company.get("page_id", "N/A")}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("Select", key=f"select_{company['page_id']}"):
                        st.session_state.selected_company = company
                        st.session_state.page_id = company["page_id"]
                        st.session_state.ads_data = None
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        elif "searchResults" not in data:
            st.markdown('<div class="empty-state">No results found. Try a different search term.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">Error loading results. Please try again.</div>', unsafe_allow_html=True)
    elif submit_button and not query:
        st.warning("Please enter a search term")

else:  # Enter Page ID tab
    with st.form("page_id_form"):
        page_id = st.text_input("Enter Facebook Page ID", 
                              placeholder="e.g. 51212153078 (Nike Football)", 
                              key="page_id_input_widget")
        submit_page_id = st.form_submit_button("🚀 Fetch Ads")
    
    if submit_page_id:
        page_id = st.session_state.page_id_input_widget
        if page_id:
            st.session_state.page_id = page_id
            st.session_state.selected_company = None
            st.session_state.ads_data = None
        else:
            st.warning("Please enter a Page ID")

# Display ads section
if st.session_state.page_id:
    st.markdown(f'<div class="section-title">📊 Ads for Page ID: {st.session_state.page_id}</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_company:
        company = st.session_state.selected_company
        col1, col2 = st.columns([1, 4])
        with col1:
            if company.get("image_uri"):
                try:
                    image = Image.open(io.BytesIO(requests.get(company["image_uri"]).content))
                    st.image(image, width=100)
                except:
                    st.image("https://via.placeholder.com/100?text=No+Image", width=100)
            else:
                st.image("https://via.placeholder.com/100?text=No+Image", width=100)
        with col2:
            st.markdown(f'<div style="font-size: 24px; font-weight: bold;">{company.get("name", "N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color: #4B4F56; margin-bottom: 15px;">{company.get("category", "N/A")} • {company.get("entity_type", "N/A").replace("_", " ").title()}</div>', unsafe_allow_html=True)
            
            col3, col4, col5 = st.columns(3)
            with col3:
                st.markdown(f'<div class="pill">👍 {company.get("likes", 0)} Likes</div>', unsafe_allow_html=True)
            with col4:
                ig_followers = company.get("ig_followers")
                if ig_followers is not None:
                    st.markdown(f'<div class="pill">📷 {ig_followers} IG Followers</div>', unsafe_allow_html=True)
            with col5:
                page_alias = company.get("page_alias")
                if page_alias:
                    st.markdown(f'<div class="pill">🔗 fb.com/{page_alias}</div>', unsafe_allow_html=True)
    
    # Fetch and display ads
    if st.session_state.ads_data is None and st.session_state.page_id:
        with st.spinner(f"Fetching ads for Page ID: {st.session_state.page_id}..."):
            ads_data = fetch_ads_data(st.session_state.page_id)
            st.session_state.ads_data = ads_data
    
    if st.session_state.ads_data:
        if "results" in st.session_state.ads_data and st.session_state.ads_data["results"]:
            active_ads = sum(1 for ad in st.session_state.ads_data["results"] if ad.get("is_active"))
            platforms = set()
            for ad in st.session_state.ads_data["results"]:
                platforms.update(ad.get("publisher_platform", []))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="pill">📋 {len(st.session_state.ads_data["results"])} Total Ads</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="pill">🟢 {active_ads} Active Ads</div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="pill">🌐 {", ".join(platforms) if platforms else "No Platform Data"}</div>', unsafe_allow_html=True)
            
            # Display ads in 2-column grid
            ads = st.session_state.ads_data["results"]
            st.markdown('<div class="ads-grid">', unsafe_allow_html=True)
            
            for i, ad in enumerate(ads):
                display_ad_card(ad, i)
                
                # Break into new rows every 2 ads
                if (i + 1) % 2 == 0:
                    st.markdown('</div><div class="ads-grid">', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No ads found for this Page ID</div>', unsafe_allow_html=True)
    elif st.session_state.page_id:
        st.warning("Could not fetch ads data. Please check the Page ID and try again.")

# Add some space at the bottom
st.write("")
st.write("")
import streamlit as st
from persona_generator import *
import os
from datetime import datetime
import base64
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Reddit Persona Generator",
    page_icon="👤",
    layout="wide"
)

# Initialize APIs
try:
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        st.error("OPENAI_API_KEY not found in environment variables")
except Exception as e:
    st.error(f"Error initializing APIs: {str(e)}")

# UI Elements
st.title("👤 Reddit User Persona Generator")
st.caption("Create detailed user personas from Reddit profiles")

with st.sidebar:
    st.header("Configuration")
    st.info("""
    **How to use:**
    1. Enter Reddit profile URL
    2. Click Generate Persona
    3. View/download results
    """)
    
    # Display current environment status
    st.divider()
    st.subheader("API Status")
    reddit_status = "✅ Configured" if os.getenv('REDDIT_CLIENT_ID') else "❌ Missing"
    openai_status = "✅ Configured" if os.getenv('OPENAI_API_KEY') else "❌ Missing"
    st.write(f"Reddit API: {reddit_status}")
    st.write(f"OpenAI API: {openai_status}")
    
    st.divider()
    st.caption("Note: Requires Reddit API credentials and OpenAI API key")
    st.link_button("Create Reddit App", "https://www.reddit.com/prefs/apps")
    st.link_button("Get OpenAI Key", "https://platform.openai.com/api-keys")

# Profile input
url = st.text_input(
    "Enter Reddit Profile URL:",
    placeholder="https://www.reddit.com/user/username/",
    help="Full URL of the Reddit profile to analyze"
)

# Add example URLs
st.caption("Example URLs:")
st.code("https://www.reddit.com/user/Hungry-Move-6603/\nhttps://www.reddit.com/user/kojied/")

if st.button("Generate Persona", type="primary"):
    if not url:
        st.warning("Please enter a Reddit profile URL")
        st.stop()
    
    with st.spinner("Extracting username..."):
        username = extract_username(url)
        
        if not username:
            st.error("""
            **Invalid Reddit URL format.**  
            Please use one of these formats:
            - https://www.reddit.com/user/username
            - https://www.reddit.com/u/username
            - https://reddit.com/user/username
            """)
            st.stop()
            
        st.info(f"Analyzing profile for: u/{username}")
        
        try:
            # Initialize Reddit
            reddit = initialize_reddit()
            
            with st.spinner(f"Scraping content for u/{username}..."):
                user = reddit.redditor(username)
                content = get_user_content(user)
                
                if not content:
                    st.warning(f"No public content found for user: u/{username}")
                    st.stop()
                
                with st.spinner("Generating persona using AI..."):
                    persona_text = generate_persona(content, username)
                
                if not persona_text or "Error" in persona_text:
                    st.error("Failed to generate persona. Please try another profile.")
                    st.stop()
                
                # Display results
                st.subheader(f"Persona for u/{username}")
                st.text_area("Persona Details", persona_text, height=500)
                
                # Save to file
                filename = save_persona_file(persona_text, username)
                
                # Download button
                with open(filename, "rb") as f:
                    st.download_button(
                        label="Download Persona",
                        data=f,
                        file_name=filename,
                        mime="text/plain",
                        use_container_width=True
                    )
                
                st.success("Persona generated successfully!")
                
        except Exception as e:
            st.error(f"Error processing profile: {str(e)}")
            st.info("""
            **Common solutions:**
            1. Verify your Reddit API credentials in .env file
            2. Check the username is correct
            3. Ensure the user has public content
            """)

# Footer
st.divider()
st.caption("""
**Assignment Notes:**
- Generates personas in the exact format from the example
- Includes citations for all persona attributes
- Follows Reddit API rate limits
- Uses GPT-3.5 for persona generation
""")
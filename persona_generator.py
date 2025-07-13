import praw
import openai
import os
from datetime import datetime
import re
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_reddit():
    # Verify credentials are present
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Missing environment variable: {var}")
    
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )

def extract_username(url):
    """Extract username from various Reddit URL formats"""
    # Handle different URL patterns
    patterns = [
        r'https?://www\.reddit\.com/user/([^/]+)/?',
        r'https?://reddit\.com/user/([^/]+)/?',
        r'https?://www\.reddit\.com/u/([^/]+)/?',
        r'https?://reddit\.com/u/([^/]+)/?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Try to extract from comment/post URLs
    if '/comments/' in url:
        parts = url.split('/')
        if len(parts) > 4 and parts[4] == 'user':
            return parts[5]
    
    return None

def get_user_content(user):
    """Scrape user comments and submissions with rate limiting"""
    content = []
    
    try:
        # Get comments
        for comment in user.comments.new(limit=100):
            content.append({
                "type": "comment",
                "text": comment.body,
                "url": f"https://reddit.com{comment.permalink}",
                "created": comment.created_utc
            })
            time.sleep(0.1)  # Rate limiting
        
        # Get submissions
        for submission in user.submissions.new(limit=50):
            content.append({
                "type": "submission",
                "text": f"{submission.title}\n{submission.selftext}",
                "url": f"https://reddit.com{submission.permalink}",
                "created": submission.created_utc
            })
            time.sleep(0.1)
    
    except Exception as e:
        print(f"Error fetching content: {e}")
    
    return sorted(content, key=lambda x: x['created'], reverse=True)

def generate_persona(content, username):
    """Generate persona using OpenAI with citations"""
    if not content:
        return "No content available for this user", []
    
    # Prepare context for LLM
    context = "\n\n".join([
        f"{item['text']}\n[Source: {item['url']}]" 
        for item in content[:10]  # Use most recent 10 items
    ])
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're an expert analyst creating detailed user personas from online content. Use the exact format from the example persona."},
                {"role": "user", "content": f"""
                Create a detailed user persona based on this Reddit activity for user {username}. 
                Follow EXACTLY this format:

                [Username]
                **AGE | OCCUPATION | STATUS | LOCATION | ARCHETYPE**

                [Personality Traits]

                MOTIVATIONS
                - [Motivation 1] (Source: URL)
                - [Motivation 2] (Source: URL)

                BEHAVIOR & HABITS
                - [Behavior 1] (Source: URL)
                - [Behavior 2] (Source: URL)

                GOALS & NEEDS
                - [Goal 1] (Source: URL)
                - [Goal 2] (Source: URL)

                FRUSTRATIONS
                - [Frustration 1] (Source: URL)
                - [Frustration 2] (Source: URL)

                "A representative quote"

                Content:
                {context}
                """}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message['content'].strip()
    
    except Exception as e:
        return f"Error generating persona: {e}", []

def save_persona_file(persona_text, username):
    """Save persona to text file"""
    filename = f"{username}_persona_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w') as f:
        f.write(f"Reddit User Persona Analysis\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(persona_text)
    return filename
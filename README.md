# Reddit User Persona Generator

This application generates detailed user personas from Reddit profiles.

## Setup

1. Create virtual environment:

python -m venv venv

source venv/bin/activate  # Linux/Mac

venv\Scripts\activate    # Windows


2. Install dependencies:

pip install -r requirements.txt


3. Create .env file with your credentials:

REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=your_app_name
OPENAI_API_KEY=your_openai_key

3. Run the code 

streamlit run app.py



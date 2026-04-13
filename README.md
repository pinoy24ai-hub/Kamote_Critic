# Kamote Critic

Kamote Critic is a Streamlit web app that reviews writing samples with a sharp but constructive academic voice.

## Features

- Review plain text, article URLs, or PDF files
- Get a structured critique with clear next steps
- Use a mobile-friendly web UI

## Local run

1. Create `.streamlit/secrets.toml`
2. Add your Gemini API key:

```toml
GEMINI_API_KEY = "your-real-key"
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run the app:

```powershell
streamlit run kamote.py
```

Or double-click `kamote_launch.bat`.

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository
2. In Streamlit Community Cloud, create a new app from that repo
3. Set the main file path to `kamote.py`
4. Add `GEMINI_API_KEY` in the app's Secrets settings
5. Deploy and open the generated URL on mobile or desktop

## Files

- `kamote.py` - the main app
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit theme and server config
- `kamote_launch.bat` - Windows launcher

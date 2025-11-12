# Quick Start Guide

Get your Derby City Watch Chatbot running in 5 minutes!

## Step 1: Get an API Key

### Option A: Gemini (Free - Recommended)

1. Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key

### Option B: OpenAI

1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up/Login
3. Create new API key
4. Copy the key

## Step 2: Configure

```bash
cd chatbot
cp .env.example .env
```

Edit `.env` and add your API key:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=paste_your_key_here
```

## Step 3: Run

### Easy Way (Linux/Mac):

```bash
chmod +x run.sh
./run.sh
```

### Manual Way:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

## Step 4: Use

Open your browser to: `http://localhost:5000`

Try asking:
- "What's happening on Bardstown Road?"
- "Any traffic on I-65?"
- "Recent fire calls?"

## Troubleshooting

**Can't connect?**
- Check your API key is valid
- Make sure .env file exists in chatbot directory

**No incidents loading?**
- The _posts directory should be at `../_posts` relative to chatbot folder
- Check POSTS_DIRECTORY setting in .env

**Need help?**
- Check the full README.md
- Verify all dependencies installed: `pip list`

## Deploy to Production

### Render.com (Easiest):

1. Create account at [render.com](https://render.com)
2. New Web Service → Connect Git
3. Add environment variables from your .env
4. Click "Create Web Service"
5. Done! You'll get a public URL

### Docker:

```bash
docker build -t derby-chatbot .
docker run -p 5000:5000 --env-file .env derby-chatbot
```

## Next Steps

- Customize the UI in `static/css/style.css`
- Modify AI behavior in `ai_service.py`
- Add custom features to `scanner_parser.py`

Enjoy your chatbot! 🚨

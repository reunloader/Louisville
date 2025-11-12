# Derby City Watch Chatbot

An AI-powered chatbot that allows users to query real-time Louisville scanner updates for public safety incidents, traffic, and emergency responses.

## Features

- **AI-Powered Chat Interface**: Natural language queries about incidents and locations
- **Switchable AI Providers**: Choose between Gemini (free tier) or OpenAI
- **Location-Based Search**: Ask about specific locations, streets, or neighborhoods
- **Route Traffic Search**: Check for incidents along routes between locations
- **Real-Time Data**: Automatically parses scanner updates from the Derby City Watch feed
- **Clean, Modern UI**: Mobile-responsive chat interface
- **Private Code**: Can be deployed separately while keeping source code private

## Architecture

```
chatbot/
├── app.py                 # Flask web application
├── scanner_parser.py      # Parses markdown scanner updates
├── ai_service.py          # Handles Gemini/OpenAI integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── templates/
│   └── index.html        # Chat interface template
└── static/
    ├── css/
    │   └── style.css     # Styles
    └── js/
        └── app.js        # Frontend logic
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- API key for Gemini or OpenAI

### 2. Installation

```bash
cd chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Choose AI provider: "gemini" or "openai"
AI_PROVIDER=gemini

# Add your API key (only the one you're using)
GEMINI_API_KEY=your_actual_gemini_api_key_here
# OPENAI_API_KEY=your_actual_openai_api_key_here

# Flask settings
FLASK_ENV=production
SECRET_KEY=your_random_secret_key_here

# Path to scanner updates (relative to chatbot directory)
POSTS_DIRECTORY=../_posts
```

### 4. Get API Keys

#### For Gemini (Free Tier - Recommended)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in `.env` as `GEMINI_API_KEY`

#### For OpenAI

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key and paste it in `.env` as `OPENAI_API_KEY`

### 5. Run the Application

```bash
python app.py
```

The chatbot will be available at `http://localhost:5000`

## Switching Between AI Providers

To switch between Gemini and OpenAI, simply change the `AI_PROVIDER` in your `.env` file:

```env
AI_PROVIDER=gemini  # or "openai"
```

Then restart the application.

## Usage Examples

Once running, try asking the chatbot:

- "What's happening around Bardstown Road?"
- "Any traffic incidents on I-65?"
- "Are there any recent fire calls in downtown Louisville?"
- "What happened on Main Street today?"
- "Traffic from Downtown to St. Matthews?"
- "Show me recent police activity"

## Deployment Options

### Option 1: Deploy with Render (Free)

1. Create account at [Render.com](https://render.com)
2. Create new Web Service
3. Connect your repository (or upload chatbot directory)
4. Set environment variables in Render dashboard
5. Deploy!

### Option 2: Deploy with Railway (Simple)

1. Create account at [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables
5. Railway will auto-deploy

### Option 3: Deploy with Docker

```dockerfile
# Create Dockerfile in chatbot directory
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t derby-chatbot .
docker run -p 5000:5000 --env-file .env derby-chatbot
```

### Option 4: Traditional VPS (DigitalOcean, Linode, etc.)

1. SSH into your server
2. Clone repository
3. Follow setup instructions above
4. Use systemd or supervisor to keep app running
5. Set up nginx as reverse proxy

## Keeping Code Private

Since you want to keep code private while the chatbot is public:

### Method 1: Private Repository + Platform Deployment

1. Keep your repository private on GitHub
2. Deploy to Render/Railway using private repo connection
3. Only the deployed chatbot URL is public

### Method 2: Deploy Compiled/Obfuscated Code

1. Use PyInstaller to compile Python code to executable
2. Deploy the compiled version
3. Source code stays on your machine

### Method 3: Separate Deployment Repository

1. Keep this code private
2. Create a separate deployment-only repository with just compiled/built files
3. Deploy from the public deployment repo

## API Endpoints

- `GET /` - Chat interface
- `POST /api/chat` - Send message, get AI response
- `POST /api/reload` - Reload scanner data
- `GET /api/stats` - Get statistics
- `POST /api/clear` - Clear conversation
- `GET /health` - Health check

## Customization

### Change Chat Appearance

Edit `static/css/style.css` to customize colors, fonts, and layout.

### Modify System Prompt

Edit the `_build_system_prompt()` method in `ai_service.py` to change how the AI responds.

### Adjust Data Parsing

Modify `scanner_parser.py` to change how incidents are extracted from markdown files.

## Troubleshooting

### "No module named 'google.generativeai'"

```bash
pip install google-generativeai
```

### "API key not found"

Make sure your `.env` file is in the `chatbot/` directory and contains your API key.

### "No scanner updates loaded"

Check that `POSTS_DIRECTORY` in `.env` points to the correct location of `_posts/` directory.

### Chat not responding

1. Check browser console for errors (F12)
2. Check Flask terminal for error messages
3. Verify API key is valid
4. Check network connectivity

## Cost Information

### Gemini Free Tier
- 60 requests per minute
- Free up to rate limit
- Perfect for personal use and small deployments

### OpenAI
- Pay per token
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- Estimate: ~$0.01-0.05 per conversation

## Security Notes

- Never commit `.env` file to git
- Keep API keys secret
- Use environment variables for production
- Consider rate limiting for public deployments
- Regularly update dependencies

## License

This chatbot is part of the Derby City Watch project.

## Support

For issues or questions, please check the main Derby City Watch repository.

# Deploying Chatbot Publicly While Keeping Code Private

This guide shows you how to deploy your chatbot for public use while keeping your source code private.

## Strategy 1: Use Platform Deployment with Private Repo (Recommended)

### Render.com with Private Repository

1. **Keep your repo private** on GitHub
2. Go to [Render.com](https://render.com) and create account
3. Click "New +" → "Web Service"
4. Click "Connect GitHub" and authorize Render
5. Select your **private** Louisville repository
6. Configure:
   ```
   Name: derby-chatbot
   Root Directory: chatbot
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```
7. Add Environment Variables:
   ```
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_key_here
   SECRET_KEY=random_secret_here
   POSTS_DIRECTORY=../_posts
   ```
8. Click "Create Web Service"

**Result**: Your code stays private on GitHub, but Render can access and deploy it. Public users only see the deployed chatbot URL.

### Railway.app with Private Repository

1. Keep repo private on GitHub
2. Go to [Railway.app](https://railway.app)
3. "New Project" → "Deploy from GitHub repo"
4. Select your private repo
5. Railway auto-detects Python app
6. Add environment variables in Railway dashboard
7. Deploy!

**Result**: Same as Render - code is private, chatbot is public.

## Strategy 2: Compiled/Binary Distribution

Build your Python app into an executable that doesn't expose source code:

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile app.py

# This creates a 'dist' folder with your executable
# Deploy only the dist folder - no source code visible
```

**Limitations**:
- Large file size
- May need separate builds for different OS
- More complex to update

## Strategy 3: Docker Container Deployment

Containers hide implementation details from end users:

```bash
# Build container
docker build -t derby-chatbot .

# Push to Docker Hub or private registry
docker push yourusername/derby-chatbot:latest

# Deploy container anywhere
# Users can't see source code inside the container
```

Deploy to:
- **Render** (supports Docker)
- **Railway** (supports Docker)
- **Fly.io** (Docker-first platform)
- **Google Cloud Run**
- **AWS ECS**
- **Azure Container Instances**

## Strategy 4: Serverless Functions

Deploy backend as serverless functions (code not directly accessible):

### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd chatbot
vercel --prod
```

### AWS Lambda + API Gateway

Package your Flask app for Lambda using Zappa or Serverless framework.

## Strategy 5: VPS with No Public Repo

Most private option:

1. Get a VPS (DigitalOcean, Linode, Vultr)
2. SSH into server
3. Upload code directly via SCP/SFTP (not via git)
4. Configure nginx reverse proxy
5. Run with systemd

**No repository at all** - code only exists on your machine and server.

## Recommended Approach for Your Use Case

Given you want:
- ✓ Code private
- ✓ Chatbot public
- ✓ Easy to update

**I recommend: Render.com with Private GitHub Repo**

### Why?
1. **Private code**: Repo stays private, only you and Render can see it
2. **Public chatbot**: Anyone can use the deployed URL
3. **Easy updates**: Push to GitHub → Auto-deploys
4. **Free tier**: Render has a generous free tier
5. **No DevOps**: Render handles infrastructure

## Setup Steps (Detailed)

### 1. Make Sure Repo is Private

```bash
# Check if repo is private
gh repo view reunloader/Louisville --json isPrivate

# Make it private if it isn't
gh repo edit reunloader/Louisville --visibility private
```

### 2. Create Render Account

- Go to https://render.com
- Sign up with GitHub
- Authorize Render to access your repositories

### 3. Create Web Service

- Click "New" → "Web Service"
- Select "reunloader/Louisville"
- Settings:
  ```
  Name: derby-city-watch-chatbot
  Region: Choose closest to you
  Branch: claude/chatbot-location-traffic-site-011CV3NceaZHfqYqvJSgPyXQ
  Root Directory: chatbot
  Runtime: Python 3
  Build Command: pip install -r requirements.txt
  Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 app:app
  ```

### 4. Environment Variables

Add in Render dashboard:

```
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
SECRET_KEY=generate_random_key_here
POSTS_DIRECTORY=../_posts
FLASK_ENV=production
```

### 5. Deploy

Click "Create Web Service" - Render will:
- Clone your private repo
- Install dependencies
- Start the app
- Give you a public URL like: `https://derby-city-watch-chatbot.onrender.com`

### 6. Share Only the URL

Give users only: `https://your-app.onrender.com`

They can use the chatbot but cannot see your code.

## Security Checklist

- [ ] Repository is private on GitHub
- [ ] .env file is in .gitignore (never committed)
- [ ] API keys are in environment variables, not hardcoded
- [ ] Only trusted users have GitHub repo access
- [ ] Deployment platform (Render/Railway) uses env vars
- [ ] No sensitive data in error messages
- [ ] Consider adding rate limiting for public chatbot
- [ ] Monitor API usage to prevent abuse

## Cost Considerations

### Free Tiers

**Render Free Tier**:
- 750 hours/month (enough for 24/7)
- Sleeps after 15 min inactivity
- Wakes up on request (slight delay)

**Railway Free Tier**:
- $5 credit/month
- No sleep
- More responsive

**Gemini Free Tier**:
- 60 requests/minute
- Perfect for personal/small use

### Upgrading

If you get lots of traffic:
- Render Starter: $7/month
- Railway: Pay as you grow
- OpenAI: Switch to paid API

## Updating Your Chatbot

With Render/Railway + GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update chatbot feature"
git push

# Auto-deploys to production!
```

## Alternative: Separate Public/Private Repos

1. **Private repo**: Full source code (this repo)
2. **Public repo**: Just documentation, issues
3. **Deployed app**: From private repo

This way users can report issues on public repo without seeing code.

## Questions?

- **Q: Can users view source via browser DevTools?**
  - A: They see frontend HTML/CSS/JS, but NOT Python backend code

- **Q: Is the API code visible?**
  - A: No, server-side Python code is not accessible to users

- **Q: Can I still use GitHub Actions?**
  - A: Yes! Actions run on private repos too

- **Q: What if I want completely zero source code online?**
  - A: Use Strategy 5 (VPS with direct upload, no git)

---

**Bottom Line**: Use Render.com or Railway.app with your private GitHub repo. Code stays private, chatbot is public, updates are automatic. Perfect balance!

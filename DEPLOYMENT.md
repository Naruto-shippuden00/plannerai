# 🚀 PlannerAI - Deployment Guide

## Railway.app Deployment (Recommended)

### Prerequisites
- Railway account
- GitHub repository
- Telegram Bot Token
- Groq API Key

### Step 1: Prepare Repository
```bash
git add .
git commit -m "Production ready - v2.1.0"
git push origin main
```

### Step 2: Railway Setup
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python

### Step 3: Environment Variables
Add these in Railway dashboard:

```env
BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
ADMIN_USER_ID=your_telegram_id
PORT=8080
PYTHONUNBUFFERED=1
TZ=Asia/Tashkent
```

### Step 4: Configure Start Command
In Railway settings:
```
Start Command: python bot.py
```

### Step 5: Deploy
Railway will automatically deploy on git push.

---

## Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Heroku account

### Setup
```bash
# Login
heroku login

# Create app
heroku create plannerai-bot

# Add buildpack
heroku buildpacks:set heroku/python

# Set env vars
heroku config:set BOT_TOKEN=your_token
heroku config:set GROQ_API_KEY=your_key
heroku config:set ADMIN_USER_ID=your_id
heroku config:set TZ=Asia/Tashkent

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

---

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Create data directories
RUN mkdir -p data/photos data/focus_photos data/charts

# Set timezone
ENV TZ=Asia/Tashkent
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Run
CMD ["python", "bot.py"]
```

### Build & Run
```bash
# Build
docker build -t plannerai .

# Run
docker run -d \
  --name plannerai-bot \
  -e BOT_TOKEN=your_token \
  -e GROQ_API_KEY=your_key \
  -e ADMIN_USER_ID=your_id \
  -v $(pwd)/data:/app/data \
  plannerai
```

---

## VPS Deployment (Ubuntu)

### Prerequisites
- Ubuntu 20.04+ VPS
- Root or sudo access

### Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3-pip python3-venv -y

# Clone repository
git clone https://github.com/yourusername/plannerai.git
cd plannerai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your tokens

# Create systemd service
sudo nano /etc/systemd/system/plannerai.service
```

### Systemd Service
```ini
[Unit]
Description=PlannerAI Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/plannerai
Environment="PATH=/home/ubuntu/plannerai/venv/bin"
ExecStart=/home/ubuntu/plannerai/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable plannerai

# Start service
sudo systemctl start plannerai

# Check status
sudo systemctl status plannerai

# View logs
sudo journalctl -u plannerai -f
```

---

## Environment Variables

### Required
- `BOT_TOKEN` - Telegram Bot token from @BotFather
- `GROQ_API_KEY` - Groq AI API key from groq.com
- `ADMIN_USER_ID` - Your Telegram user ID

### Optional
- `PORT` - Port for webhook (default: 8080)
- `TZ` - Timezone (default: Asia/Tashkent)
- `PYTHONUNBUFFERED` - Set to 1 for better logging
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

---

## Database Management

### Backup
```bash
# Backup database
cp data/productivity.db data/backup_$(date +%Y%m%d).db

# Backup photos
tar -czf photos_backup_$(date +%Y%m%d).tar.gz data/photos data/focus_photos
```

### Restore
```bash
# Restore database
cp data/backup_20260613.db data/productivity.db

# Restore photos
tar -xzf photos_backup_20260613.tar.gz
```

---

## Monitoring

### Health Check
```bash
# Check if bot is running
curl http://localhost:8080/health

# Check logs
tail -f data/bot.log
```

### Metrics
- Active users
- Tasks completed
- Focus sessions
- Notifications sent
- Error rate

---

## Security

### Best Practices
1. Never commit .env file
2. Use strong passwords
3. Regular backups
4. Monitor logs for suspicious activity
5. Keep dependencies updated

### Firewall
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS (if using webhook)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

---

## Troubleshooting

### Bot not responding
```bash
# Check if process is running
ps aux | grep bot.py

# Check logs
tail -f data/bot.log

# Restart service
sudo systemctl restart plannerai
```

### Database locked
```bash
# Stop bot
sudo systemctl stop plannerai

# Backup database
cp data/productivity.db data/backup.db

# Restart bot
sudo systemctl start plannerai
```

### Memory issues
```bash
# Check memory usage
free -h

# Check bot memory
ps aux | grep bot.py

# Restart bot to clear memory
sudo systemctl restart plannerai
```

---

## Scaling

### Multiple Instances
For high load, use multiple bot instances with webhook mode:

1. Use nginx as load balancer
2. Run multiple bot processes
3. Use Redis for session storage
4. Use PostgreSQL instead of SQLite

### Webhook Mode
```python
# In bot.py
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

async def on_startup(bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
setup_application(app, dp, bot=bot)

web.run_app(app, host="0.0.0.0", port=8080)
```

---

## Maintenance

### Regular Tasks
- Daily: Check logs for errors
- Weekly: Backup database
- Monthly: Update dependencies
- Quarterly: Review and optimize

### Updates
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart bot
sudo systemctl restart plannerai
```

---

## Support

For issues or questions:
- GitHub Issues: [Report a bug](https://github.com/yourusername/plannerai/issues)
- Email: support@plannerai.com
- Telegram: @YourUsername

---

**Last Updated:** 2026-06-13  
**Version:** 2.1.0  
**Status:** Production Ready ✅

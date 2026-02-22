# 🚀 Deployment Guide

## Quick Deploy to Render.com

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Living Ledger"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/living-ledger.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your `living-ledger` repository
5. Configure:
   - **Build Command**: `cd living_ledger && pip install -r requirements.txt`
   - **Start Command**: `cd living_ledger && uvicorn api:app --host 0.0.0.0 --port $PORT`
6. Click "Create Web Service"
7. Wait 5-10 minutes

### Step 3: Access Your Live App

```
https://your-app.onrender.com
```

## Alternative Platforms

### Railway.app
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Heroku
```bash
heroku login
heroku create living-ledger-app
git push heroku main
heroku open
```

## Environment Variables (Optional)

```
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

## After Deployment

1. Visit your live URL
2. Login as admin (admin@livingledger.com / Admin@123)
3. **Change the default admin password immediately!**
4. Test all features

## Troubleshooting

- **404 errors**: Check build/start commands
- **Module not found**: Verify requirements.txt
- **Database issues**: SQLite works automatically
- **Static files**: Already configured in api.py

---

See README.md for complete documentation.

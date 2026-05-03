# Render Deployment Guide

## Prerequisites
- GitHub repository with the code
- Render account (https://render.com)
- Groq API key

## Step-by-Step Deployment

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Deploy Backend on Render

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. **Service Configuration**:
   - **Name**: sap-o2c-backend
   - **Runtime**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python main.py`
   - **Instance Type**: Free

5. **Environment Variables**:
   - `GROQ_API_KEY`: Your Groq API key
   - `PORT`: `10000` (Render's default)

6. Click **Create Web Service**

### 3. Deploy Frontend on Render

1. Click **New +** → **Static Site**
2. Connect your GitHub repository
3. **Service Configuration**:
   - **Name**: sap-o2c-frontend
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Node Version**: `18` (or latest)

4. **Environment Variables**:
   - `VITE_API_URL`: `https://sap-o2c-backend.onrender.com`

5. **Advanced Settings** → **Custom Rewrites**:
   - **Source**: `/api/*`
   - **Destination**: `https://sap-o2c-backend.onrender.com/*`

6. Click **Create Static Site**

### 4. Verify Deployment

1. Backend will be available at: `https://sap-o2c-backend.onrender.com`
2. Frontend will be available at: `https://sap-o2c-frontend.onrender.com`
3. Test the health endpoint: `https://sap-o2c-backend.onrender.com/health`

### 5. Troubleshooting

#### Backend Issues
- Check logs in Render dashboard
- Verify GROQ_API_KEY is set correctly
- Ensure all dependencies are in requirements.txt

#### Frontend Issues
- Check that build completes successfully
- Verify API URL is correct in environment variables
- Check CORS configuration in backend

#### Common Problems
- **Build fails**: Check package.json and requirements.txt
- **API errors**: Verify backend URL and CORS settings
- **Data loading**: Ensure data files are included in repository

## Automatic Deployment (render.yaml)

The repository includes `render.yaml` for automatic deployment:

1. Go to Render Dashboard
2. Click **New +** → **Blueprint**
3. Connect your GitHub repository
4. Render will automatically create both services from the YAML file
5. Add your GROQ_API_KEY when prompted

## Environment Variables

### Backend
- `GROQ_API_KEY`: Required for LLM functionality
- `PORT`: Render port (default: 10000)

### Frontend
- `VITE_API_URL`: Backend URL for API calls

## Cost

- **Free Tier**: Both services can run on Render's free tier
- **Limitations**: Free tier spins down after 15 minutes of inactivity
- **Upgrade**: Paid plans available for production use

## Support

- Render documentation: https://render.com/docs
- Repository issues: Check GitHub Issues
- Status page: https://status.render.com

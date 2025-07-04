# Render Deployment Guide

This guide provides step-by-step instructions to deploy the Phygital Facility Manager application on Render and add a custom domain.

## Project Structure
- **Frontend**: React + TypeScript + Vite application in `/frontend`
- **Backend**: Flask Python API in `/backend`
- **Database**: Neon PostgreSQL with pgvector extension

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be pushed to a GitHub repository
3. **Neon Database**: Set up your Neon PostgreSQL database
4. **Domain**: Have your custom domain ready (optional)

## Step 1: Prepare Your Repository

### 1.1 Create Root-Level Configuration Files

Create these files in your project root (`phygital-facility-manager/`):

#### `render.yaml` (Optional - for Infrastructure as Code)
```yaml
services:
  - type: web
    name: facility-manager-backend
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && gunicorn app:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_ENV
        value: production

  - type: web
    name: facility-manager-frontend
    env: node
    buildCommand: "cd frontend && npm ci && npm run build"
    startCommand: "cd frontend && npm run preview"
    envVars:
      - key: NODE_VERSION
        value: 18
```

### 1.2 Update Backend for Production

Ensure your `backend/app.py` has proper production configuration:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 1.3 Create Backend Build Script

Create `backend/build.sh`:
```bash
#!/bin/bash
pip install -r requirements.txt
```

### 1.4 Update Frontend for Production

Update `frontend/vite.config.ts` to handle production API URL:

```typescript
export default defineConfig({
  plugins: [react(), VitePWA({...})],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  preview: {
    port: 4173,
    host: true
  }
});
```

## Step 2: Deploy Backend to Render

### 2.1 Create Web Service for Backend

1. **Login to Render Dashboard**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Connect Repository**
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your repository

3. **Configure Backend Service**
   - **Name**: `facility-manager-backend`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Set Environment Variables**
   Click "Advanced" and add these environment variables:
   ```
   FLASK_ENV=production
   DATABASE_URL=your_neon_database_url
   OPENAI_API_KEY=your_openai_api_key
   CLICKUP_API_TOKEN=your_clickup_token
   CLICKUP_TEAM_ID=your_clickup_team_id
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   SECRET_KEY=your_flask_secret_key
   FIREFLY_URL=your_firefly_instance_url
   FIREFLY_TOKEN=your_firefly_api_token
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)
   - Note the service URL (e.g., `https://facility-manager-backend.onrender.com`)

## Step 3: Deploy Frontend to Render

### 3.1 Create Web Service for Frontend

1. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Select same repository

2. **Configure Frontend Service**
   - **Name**: `facility-manager-frontend`
   - **Environment**: `Node`
   - **Region**: Same as backend
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Start Command**: `npm run preview`

3. **Set Environment Variables**
   ```
   NODE_VERSION=18
   VITE_API_URL=https://facility-manager-backend.onrender.com
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the service URL (e.g., `https://facility-manager-frontend.onrender.com`)

## Step 4: Configure CORS and API Integration

### 4.1 Update Backend CORS Settings

In your `backend/app.py`, update CORS configuration:

```python
from flask_cors import CORS

# Update CORS to allow your frontend domain
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:4173", 
    "https://facility-manager-frontend.onrender.com",
    "https://your-custom-domain.com"  # Add your custom domain
])
```

### 4.2 Update Frontend API Configuration

Create `frontend/src/config/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.DEV ? 'http://localhost:5000' : 'https://facility-manager-backend.onrender.com');

export { API_BASE_URL };
```

## Step 5: Add Custom Domain

### 5.1 Add Domain to Frontend Service

1. **Go to Frontend Service Dashboard**
   - Navigate to your frontend service in Render
   - Click "Settings" tab
   - Scroll to "Custom Domains" section

2. **Add Custom Domain**
   - Click "Add Custom Domain"
   - Enter your domain (e.g., `facility.yourdomain.com`)
   - Click "Save"

3. **Configure DNS**
   - Copy the CNAME record provided by Render
   - Go to your domain registrar's DNS settings
   - Add a CNAME record:
     - **Name**: `facility` (or your subdomain)
     - **Value**: The CNAME provided by Render
     - **TTL**: 300 (or default)

### 5.2 Add Domain to Backend Service (Optional)

If you want a custom domain for your API:

1. **Add API Subdomain**
   - Go to backend service → Settings → Custom Domains
   - Add `api.yourdomain.com`
   - Configure DNS with provided CNAME

2. **Update Frontend Configuration**
   ```typescript
   const API_BASE_URL = 'https://api.yourdomain.com';
   ```

### 5.3 SSL Certificate

- Render automatically provides SSL certificates for custom domains
- Wait 5-10 minutes after DNS propagation for SSL to activate
- Verify HTTPS is working: `https://your-domain.com`

## Step 6: Environment Variables Setup

### 6.1 Backend Environment Variables

Ensure all required environment variables are set in Render:

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# OpenAI
OPENAI_API_KEY=sk-...

# ClickUp Integration
CLICKUP_API_TOKEN=pk_...
CLICKUP_TEAM_ID=...

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Security
SECRET_KEY=your-secret-key-here

# Firefly III
FIREFLY_URL=https://your-firefly-instance.com
FIREFLY_TOKEN=...

# Flask
FLASK_ENV=production
```

### 6.2 Frontend Environment Variables

```bash
NODE_VERSION=18
VITE_API_URL=https://your-backend-domain.com
```

## Step 7: Database Setup

### 7.1 Neon Database Configuration

1. **Create Neon Database**
   - Go to [neon.tech](https://neon.tech)
   - Create a new project
   - Note the connection string

2. **Install pgvector Extension**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Run Database Migrations**
   - Use the connection string in your backend environment
   - Run your database setup scripts

## Step 8: Testing Deployment

### 8.1 Verify Services

1. **Backend Health Check**
   ```bash
   curl https://your-backend-domain.com/api/health
   ```

2. **Frontend Access**
   - Visit `https://your-frontend-domain.com`
   - Test login functionality
   - Verify API calls work

### 8.2 Monitor Logs

1. **Backend Logs**
   - Go to backend service → Logs tab
   - Monitor for errors

2. **Frontend Logs**
   - Go to frontend service → Logs tab
   - Check build and runtime logs

## Step 9: Production Optimizations

### 9.1 Performance Settings

1. **Backend Scaling**
   - Go to backend service → Settings
   - Adjust instance type if needed
   - Enable auto-scaling

2. **Frontend Caching**
   - Render automatically handles static file caching
   - Verify browser caching headers

### 9.2 Monitoring

1. **Set up Health Checks**
   - Configure health check endpoints
   - Set up monitoring alerts

2. **Performance Monitoring**
   - Monitor response times
   - Set up error tracking

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs in Render dashboard
   - Verify all dependencies are in requirements.txt/package.json

2. **Environment Variables**
   - Ensure all required env vars are set
   - Check for typos in variable names

3. **CORS Errors**
   - Update CORS origins in backend
   - Verify frontend is using correct API URL

4. **Database Connection**
   - Verify DATABASE_URL format
   - Check Neon database is accessible

### Support Resources

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- Check service logs for detailed error messages

## Maintenance

### Regular Updates

1. **Dependency Updates**
   - Regularly update package.json and requirements.txt
   - Test updates in development first

2. **Security Updates**
   - Monitor for security advisories
   - Update environment variables as needed

3. **Backup Strategy**
   - Regular database backups via Neon
   - Version control for code changes

---

**Deployment Complete!** Your application should now be accessible at your custom domain with both frontend and backend services running on Render.

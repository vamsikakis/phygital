# Render Deployment Guide for Phygital Facility Manager with Real Firefly III

This guide will help you deploy your facility management application to Render with a real Firefly III service.

## What Will Be Deployed

1. **Firefly III Service**: Real financial management service with PostgreSQL database
2. **Backend API**: Your facility management backend
3. **Frontend**: React application
4. **Databases**: Separate PostgreSQL databases for Firefly III and your application

## Prerequisites

1. ✅ **GitHub Repository**: Your code is already pushed to GitHub
2. ✅ **Neon Database**: PostgreSQL database is configured and running
3. ✅ **Environment Variables**: All API keys and secrets ready

## Deployment Steps

### Step 1: Connect GitHub to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Sign up/Login with your GitHub account
3. Grant Render access to your `phygital` repository

### Step 2: Deploy Using render.yaml (Recommended)

1. **Create New Service from Repository**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository: `vamsikakis/phygital`
   - Render will automatically detect the `render.yaml` file

2. **Configure Environment Variables**:
   The following variables need to be set manually (marked as `sync: false` in render.yaml):

   **Required Environment Variables**:
   
   Copy these values from your local `phygital-facility-manager/backend/.env` file:
   
   - `OPENAI_ORG_ID` - Your OpenAI organization ID
   - `OPENAI_API_KEY` - Your OpenAI API key  
   - `OPENAI_ASSISTANT_ID` - Your OpenAI assistant ID
   - `OPENAI_VECTOR_STORE_ID` - Your OpenAI vector store ID
   - `CLICKUP_CLIENT_ID` - Your ClickUp client ID
   - `CLICKUP_CLIENT_SECRET` - Your ClickUp client secret
   - `CLICKUP_API_TOKEN` - Your ClickUp API token
   - `CLICKUP_TEAM_ID` - Your ClickUp team ID
   - `CLICKUP_SPACE_ID` - Your ClickUp space ID
   - `CLICKUP_LIST_ID` - Your ClickUp list ID
   - `CLICKUP_FOLDER_ID` - Your ClickUp folder ID
   - `OCR_SPACE_API_KEY` - Your OCR Space API key

3. **Database Configuration**:
   - The render.yaml includes both Firefly III PostgreSQL and your Neon database
   - Firefly III will get its own dedicated database
   - Your application will continue using the existing Neon database

4. **Post-Deployment Firefly III Setup**:
   After deployment, you'll need to:
   - Access Firefly III at its deployed URL
   - Complete the initial setup wizard
   - Create a Personal Access Token
   - Add the token to your backend environment variables

### Step 3: Manual Deployment (Alternative)

If you prefer manual setup:

#### Backend Deployment:
1. **New Web Service**:
   - Repository: `vamsikakis/phygital`
   - Branch: `main`
   - Root Directory: `phygital-facility-manager/backend`
   - Environment: `Docker`
   - Dockerfile Path: `./Dockerfile`

2. **Service Configuration**:
   - Name: `phygital-backend`
   - Plan: `Starter` ($7/month)
   - Health Check Path: `/health`

#### Frontend Deployment:
1. **New Static Site**:
   - Repository: `vamsikakis/phygital`
   - Branch: `main`
   - Root Directory: `phygital-facility-manager/frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

2. **Environment Variables**:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

### Step 4: Post-Deployment Configuration

1. **Set Up Firefly III**:
   - Visit your Firefly III URL: `https://firefly-iii.onrender.com`
   - Complete the initial setup wizard
   - Create your admin account
   - Set up your financial accounts and categories

2. **Create Firefly III API Token**:
   - Login to Firefly III
   - Go to Profile → OAuth → Personal Access Tokens
   - Click "Create new token"
   - Name it "Facility Manager Integration"
   - **IMPORTANT**: UNCHECK "Confidential" checkbox
   - Copy the generated token

3. **Update Backend Environment Variables**:
   In your Render backend service, add:
   ```
   FIREFLY_API_TOKEN=your_very_long_token_from_step_2
   ```

4. **Update CORS Origins**:
   After deployment, update the backend's `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://your-frontend-url.onrender.com,http://localhost:3000
   ```

5. **Update ClickUp Redirect URI**:
   ```
   CLICKUP_REDIRECT_URI=https://your-backend-url.onrender.com/api/clickup/callback
   ```

6. **Test Deployment**:
   - Visit your frontend URL
   - Test all major features:
     - Knowledge Base document upload
     - Communication features
     - ClickUp integration
     - AI Assistant
     - **Financial Dashboard (now with REAL Firefly III data!)**

## Important Notes

### Firefly III in Cloud Deployment
- **Local Development**: Uses real Firefly III Docker container
- **Cloud Deployment**: Now uses REAL Firefly III service with dedicated PostgreSQL database
- **Data Persistence**: All financial data is stored in Render's PostgreSQL database
- **Full Features**: Complete Firefly III functionality available in the cloud

### File Storage
- Uploaded files are stored in the container's filesystem
- For production, consider using external storage (AWS S3, etc.)

### Database
- Uses your existing Neon PostgreSQL database
- No additional database setup required

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check that all dependencies are in requirements.txt
   - Verify Dockerfile syntax

2. **Environment Variables**:
   - Ensure all required variables are set
   - Check for typos in variable names

3. **CORS Errors**:
   - Update CORS_ORIGINS with correct frontend URL
   - Ensure both HTTP and HTTPS are included if needed

4. **Database Connection**:
   - Verify Neon database is accessible
   - Check DATABASE_URL format

## Expected URLs

After successful deployment:
- **Firefly III**: `https://firefly-iii.onrender.com`
- **Backend**: `https://phygital-backend.onrender.com`
- **Frontend**: `https://phygital-frontend.onrender.com`
- **Health Check**: `https://phygital-backend.onrender.com/health`

## Cost Estimate

- **Firefly III Service (Starter Plan)**: $7/month
- **Firefly III Database (Starter Plan)**: $7/month
- **Backend (Starter Plan)**: $7/month
- **Frontend (Static Site)**: Free
- **Main Database**: Using existing Neon (Free tier available)

**Total**: ~$21/month for full deployment with real Firefly III

### Cost Optimization Options:
- Use Render's free tier for development/testing
- Consider shared database plans if available
- Monitor usage and adjust plans as needed

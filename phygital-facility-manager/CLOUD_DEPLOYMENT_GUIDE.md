# Cloud Deployment Guide with Docker

This guide provides comprehensive instructions for deploying the Phygital Facility Manager application to the cloud using Docker containers, including Firefly III integration.

## 🏗️ Architecture Overview

- **Frontend**: React + TypeScript + Vite (Static files served via CDN/Web Service)
- **Backend**: Flask Python API (Containerized)
- **Database**: Neon PostgreSQL with pgvector (Cloud-hosted)
- **Financial Management**: Firefly III (Containerized)
- **File Storage**: Cloud storage integration
- **Deployment Platform**: Render (Primary), with alternatives

## 🚀 Deployment Options

### Option 1: Render (Recommended)
- **Pros**: Easy setup, automatic deployments, built-in Docker support
- **Cons**: Limited free tier
- **Best for**: Production deployments

### Option 2: Railway
- **Pros**: Excellent Docker support, generous free tier
- **Cons**: Newer platform
- **Best for**: Development and small production

### Option 3: Heroku
- **Pros**: Mature platform, extensive add-ons
- **Cons**: No free tier, more expensive
- **Best for**: Enterprise deployments

### Option 4: DigitalOcean App Platform
- **Pros**: Good pricing, Docker support
- **Cons**: Less automation than Render
- **Best for**: Custom configurations

## 📋 Prerequisites

1. **Cloud Accounts**:
   - Render account (or chosen platform)
   - Neon database account
   - GitHub repository with your code

2. **Required Services**:
   - Neon PostgreSQL database with pgvector
   - OpenAI API key
   - ClickUp API credentials (optional)
   - Google OAuth credentials (optional)

3. **Domain** (optional):
   - Custom domain for production deployment

## 🐳 Docker Configuration

### Step 1: Create Docker Files

#### Backend Dockerfile
```dockerfile
# phygital-facility-manager/backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p storage

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```

#### Frontend Dockerfile
```dockerfile
# phygital-facility-manager/frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Firefly III Docker Compose
```yaml
# phygital-facility-manager/docker-compose.firefly.yml
version: '3.8'

services:
  firefly-db:
    image: postgres:15
    environment:
      POSTGRES_DB: firefly
      POSTGRES_USER: firefly
      POSTGRES_PASSWORD: ${FIREFLY_DB_PASSWORD}
    volumes:
      - firefly_db_data:/var/lib/postgresql/data
    restart: unless-stopped

  firefly-app:
    image: fireflyiii/core:latest
    depends_on:
      - firefly-db
    environment:
      APP_KEY: ${FIREFLY_APP_KEY}
      DB_CONNECTION: pgsql
      DB_HOST: firefly-db
      DB_PORT: 5432
      DB_DATABASE: firefly
      DB_USERNAME: firefly
      DB_PASSWORD: ${FIREFLY_DB_PASSWORD}
      APP_URL: ${FIREFLY_APP_URL}
      TRUSTED_PROXIES: "**"
      APP_ENV: production
      APP_DEBUG: false
    volumes:
      - firefly_upload:/var/www/html/storage/upload
    ports:
      - "8080:8080"
    restart: unless-stopped

volumes:
  firefly_db_data:
  firefly_upload:
```

### Step 2: Create Supporting Files

#### Frontend Nginx Configuration
```nginx
# phygital-facility-manager/frontend/nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API proxy (if needed)
        location /api {
            proxy_pass http://backend:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
    }
}
```

#### Docker Compose for Development
```yaml
# phygital-facility-manager/docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FIREFLY_BASE_URL=http://firefly-app:8080
      - FIREFLY_API_TOKEN=${FIREFLY_API_TOKEN}
    volumes:
      - ./backend:/app
      - backend_storage:/app/storage
    depends_on:
      - firefly-app

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  firefly-db:
    image: postgres:15
    environment:
      POSTGRES_DB: firefly
      POSTGRES_USER: firefly
      POSTGRES_PASSWORD: ${FIREFLY_DB_PASSWORD}
    volumes:
      - firefly_db_data:/var/lib/postgresql/data

  firefly-app:
    image: fireflyiii/core:latest
    depends_on:
      - firefly-db
    environment:
      APP_KEY: ${FIREFLY_APP_KEY}
      DB_CONNECTION: pgsql
      DB_HOST: firefly-db
      DB_PORT: 5432
      DB_DATABASE: firefly
      DB_USERNAME: firefly
      DB_PASSWORD: ${FIREFLY_DB_PASSWORD}
      APP_URL: http://localhost:8080
      TRUSTED_PROXIES: "**"
    volumes:
      - firefly_upload:/var/www/html/storage/upload
    ports:
      - "8080:8080"

volumes:
  backend_storage:
  firefly_db_data:
  firefly_upload:
```

## 🔧 Environment Configuration

### Cloud Environment Variables

Create these environment variables in your cloud platform:

#### Backend Service Environment Variables
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
PORT=5000

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@hostname:5432/database

# OpenAI Integration
OPENAI_API_KEY=sk-your-openai-api-key

# ClickUp Integration (Optional)
CLICKUP_API_TOKEN=pk_your-clickup-token
CLICKUP_TEAM_ID=your-team-id

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Firefly III Integration
FIREFLY_BASE_URL=https://your-firefly-domain.com
FIREFLY_API_TOKEN=your-firefly-personal-access-token

# Security
JWT_SECRET_KEY=your-jwt-secret-key
WEBHOOK_SECRET=your-webhook-secret
```

#### Frontend Service Environment Variables
```bash
# Build Configuration
NODE_VERSION=18
VITE_API_URL=https://your-backend-domain.com

# Optional: Analytics, monitoring
VITE_ANALYTICS_ID=your-analytics-id
```

#### Firefly III Service Environment Variables
```bash
# Firefly III Configuration
FIREFLY_APP_KEY=32-character-random-string-here
FIREFLY_DB_PASSWORD=secure-database-password
FIREFLY_APP_URL=https://your-firefly-domain.com

# Database
DB_CONNECTION=pgsql
DB_HOST=firefly-db
DB_PORT=5432
DB_DATABASE=firefly
DB_USERNAME=firefly

# Security
APP_ENV=production
APP_DEBUG=false
TRUSTED_PROXIES=**
```

## 🚀 Render Deployment (Recommended)

### Step 1: Prepare Repository

1. **Push to GitHub**: Ensure all Docker files are in your repository
2. **Create .dockerignore files**:

```dockerignore
# backend/.dockerignore
__pycache__
*.pyc
.env
.venv
venv/
.git
.gitignore
README.md
tests/
.pytest_cache
```

```dockerignore
# frontend/.dockerignore
node_modules
.git
.gitignore
README.md
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

### Step 2: Deploy Backend Service

1. **Create Web Service**:
   - Go to Render Dashboard → New → Web Service
   - Connect your GitHub repository
   - Configure:
     - **Name**: `facility-manager-backend`
     - **Environment**: `Docker`
     - **Region**: Choose closest to users
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Dockerfile Path**: `backend/Dockerfile`

2. **Set Environment Variables**: Add all backend environment variables listed above

3. **Deploy**: Click "Create Web Service"

### Step 3: Deploy Firefly III Service

1. **Create Web Service**:
   - Name: `facility-manager-firefly`
   - Environment: `Docker`
   - Docker Image: `fireflyiii/core:latest`
   - Port: `8080`

2. **Add PostgreSQL Database**:
   - Go to Dashboard → New → PostgreSQL
   - Name: `firefly-database`
   - Note the connection details

3. **Configure Firefly Environment Variables**:
   ```bash
   APP_KEY=generate-32-char-random-string
   DB_CONNECTION=pgsql
   DB_HOST=your-postgres-host
   DB_PORT=5432
   DB_DATABASE=your-database-name
   DB_USERNAME=your-username
   DB_PASSWORD=your-password
   APP_URL=https://your-firefly-domain.onrender.com
   TRUSTED_PROXIES=**
   ```

### Step 4: Deploy Frontend Service

1. **Create Static Site**:
   - Go to Dashboard → New → Static Site
   - Connect repository
   - Configure:
     - **Name**: `facility-manager-frontend`
     - **Branch**: `main`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm ci && npm run build`
     - **Publish Directory**: `dist`

2. **Set Environment Variables**: Add frontend environment variables

### Step 5: Configure Custom Domains

1. **Add Custom Domains**:
   - Backend: `api.yourdomain.com`
   - Frontend: `app.yourdomain.com` or `yourdomain.com`
   - Firefly: `finance.yourdomain.com`

2. **Update DNS Records**:
   - Add CNAME records pointing to Render URLs
   - Wait for SSL certificates to provision

3. **Update Environment Variables**:
   - Update `VITE_API_URL` in frontend
   - Update `FIREFLY_BASE_URL` in backend
   - Update CORS origins in backend

## 🔒 Security Considerations

### Production Security Checklist

1. **Environment Variables**:
   - Use strong, unique passwords
   - Rotate API keys regularly
   - Never commit secrets to repository

2. **Database Security**:
   - Use SSL connections
   - Restrict database access
   - Regular backups

3. **Application Security**:
   - Enable HTTPS only
   - Configure proper CORS
   - Implement rate limiting
   - Use secure headers

4. **Firefly III Security**:
   - Use strong APP_KEY
   - Secure database connection
   - Regular updates

## 📊 Monitoring and Maintenance

### Health Checks

1. **Backend Health Endpoint**:
   ```python
   @app.route('/health')
   def health_check():
       return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow()})
   ```

2. **Firefly III Health**:
   - Monitor `/api/v1/about` endpoint
   - Check database connectivity

### Logging

1. **Application Logs**:
   - Configure structured logging
   - Use log aggregation services
   - Monitor error rates

2. **Performance Monitoring**:
   - Track response times
   - Monitor resource usage
   - Set up alerts

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render
        uses: render-deploy/github-action@v1
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Check build logs

2. **Database Connection**:
   - Verify connection string format
   - Check firewall settings
   - Test connectivity

3. **Firefly III Issues**:
   - Verify APP_KEY is 32 characters
   - Check database permissions
   - Monitor container logs

### Support Resources

- [Render Documentation](https://render.com/docs)
- [Firefly III Documentation](https://docs.firefly-iii.org)
- [Docker Documentation](https://docs.docker.com)

## 🛠️ Quick Start Deployment

### Using the Deployment Script

We've provided automated deployment scripts to simplify the process:

#### For Linux/Mac:
```bash
# Make script executable
chmod +x deploy.sh

# Check prerequisites
./deploy.sh check

# Validate configuration
./deploy.sh validate

# Test locally with Docker
./deploy.sh test

# Prepare for cloud deployment
./deploy.sh prepare
```

#### For Windows:
```cmd
# Check prerequisites
deploy.bat check

# Validate configuration
deploy.bat validate

# Test locally with Docker
deploy.bat test

# Prepare for cloud deployment
deploy.bat prepare
```

### Manual Deployment Steps

If you prefer manual deployment or need to customize the process:

1. **Copy environment template:**
   ```bash
   cp .env.production.example .env.production
   # Edit .env.production with your actual values
   ```

2. **Build and test locally:**
   ```bash
   docker-compose up -d
   # Test at http://localhost:3000
   ```

3. **Deploy to Render:**
   - Follow the detailed steps in the sections above
   - Use the environment variables from `.env.production`

## 📱 Mobile App Deployment

Your application is built as a Progressive Web App (PWA) and can be installed on mobile devices:

1. **PWA Features:**
   - Installable on iOS and Android
   - Offline functionality
   - Push notifications (if configured)
   - Native app-like experience

2. **Installation:**
   - Users can install directly from the browser
   - No app store submission required
   - Automatic updates when you deploy

## 🔄 Continuous Deployment

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Trigger Render Deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

### Automatic Deployments

- **Render**: Automatically deploys on git push to main branch
- **Railway**: Similar auto-deploy functionality
- **Manual Trigger**: Use deploy hooks for manual deployments

---

**Next Steps**: After deployment, test all functionality, set up monitoring, and configure automated backups for your databases.

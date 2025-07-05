# 🏦 Firefly III Deployment Guide for Render

This guide will help you deploy Firefly III on Render and integrate it with your Facility Manager application.

## 📋 Prerequisites

- Render account
- Your backend service already deployed
- Basic understanding of environment variables

## 🚀 Step-by-Step Deployment

### Step 1: Create PostgreSQL Database

1. **Login to Render Dashboard**: https://dashboard.render.com
2. **Create Database**:
   - Click "New +" → "PostgreSQL"
   - **Name**: `firefly-database`
   - **Database Name**: `firefly`
   - **User**: `firefly`
   - **Region**: Same as your backend
   - **Plan**: Free (for testing) or Starter+ (for production)

3. **Save Connection Details**:
   After creation, note these details:
   - **Host**: `dpg-xxxxx-a.oregon-postgres.render.com`
   - **Database**: `firefly`
   - **Username**: `firefly`
   - **Password**: `xxxxx` (auto-generated)
   - **Port**: `5432`

### Step 2: Deploy Firefly III Service

1. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Choose "Deploy an existing image from a registry"

2. **Configure Service**:
   - **Image URL**: `fireflyiii/core:latest`
   - **Service Name**: `firefly-iii-production`
   - **Region**: Same as your other services
   - **Instance Type**: Starter (minimum 512MB RAM)

3. **Environment Variables**:
   Add these environment variables:

   ```bash
   # Required App Configuration
   APP_KEY=SomeRandomStringOf32CharsExactly
   APP_ENV=production
   APP_DEBUG=false
   APP_URL=https://firefly-iii-production.onrender.com
   
   # Database Configuration (replace with your actual values)
   DB_CONNECTION=pgsql
   DB_HOST=dpg-xxxxx-a.oregon-postgres.render.com
   DB_PORT=5432
   DB_DATABASE=firefly
   DB_USERNAME=firefly
   DB_PASSWORD=your-actual-password-here
   
   # Security
   TRUSTED_PROXIES=**
   
   # Performance
   CACHE_DRIVER=file
   SESSION_DRIVER=file
   LOG_CHANNEL=stdout
   
   # Optional: Email Configuration
   MAIL_MAILER=smtp
   MAIL_HOST=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_ENCRYPTION=tls
   MAIL_FROM_ADDRESS=your-email@gmail.com
   ```

4. **Deploy**: Click "Create Web Service"

### Step 3: Initial Firefly III Setup

1. **Wait for Deployment**: 5-10 minutes
2. **Open Firefly III**: Visit your service URL
3. **Complete Setup Wizard**:
   - Create admin account
   - Set preferences
   - Configure currency (INR for India)
   - Set up initial accounts

### Step 4: Create API Token

1. **Login to Firefly III**
2. **Navigate**: Profile → OAuth → Personal Access Tokens
3. **Create Token**:
   - Click "Create new token"
   - **Name**: "Facility Manager Integration"
   - **Scopes**: Leave default (full access)
   - **Copy the token** (very long string starting with "eyJ...")

### Step 5: Update Backend Configuration

1. **Go to your backend service** in Render
2. **Update Environment Variables**:
   ```bash
   FIREFLY_BASE_URL=https://firefly-iii-production.onrender.com
   FIREFLY_API_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
   ```

3. **Redeploy**: Service will auto-redeploy with new variables

### Step 6: Test Integration

Test these endpoints:

```bash
# Test connection
curl https://phygital-s839.onrender.com/api/firefly/test

# Test summary
curl https://phygital-s839.onrender.com/api/firefly/summary

# Test accounts
curl https://phygital-s839.onrender.com/api/firefly/accounts
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify database credentials
   - Check if database is in same region
   - Ensure database is running

2. **App Key Error**
   - Generate 32-character random string
   - Use: `head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32`

3. **Memory Issues**
   - Upgrade to Starter instance type (512MB+)
   - Firefly III requires minimum 512MB RAM

4. **API Token Issues**
   - Regenerate token in Firefly III
   - Ensure token has full access
   - Check token format (should be JWT)

### Environment Variable Generator

Use this to generate a secure APP_KEY:

```bash
# Linux/Mac
head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32

# Windows PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

## 📊 Expected Results

After successful deployment:

1. **Firefly III Dashboard**: Accessible at your service URL
2. **API Integration**: Your app can create/read financial data
3. **Financial Dashboard**: Shows real data from Firefly III
4. **Budget Management**: Create and track budgets
5. **Transaction Tracking**: Record facility expenses

## 🎯 Next Steps

1. **Set up Accounts**:
   - Maintenance Fund
   - Utility Accounts
   - Vendor Payments
   - Reserve Funds

2. **Create Budgets**:
   - Monthly maintenance
   - Utility bills
   - Emergency repairs
   - Capital improvements

3. **Configure Categories**:
   - Maintenance
   - Utilities
   - Security
   - Landscaping
   - Administration

## 💡 Pro Tips

1. **Backup Strategy**: Render PostgreSQL includes automated backups
2. **Monitoring**: Set up alerts for service health
3. **Security**: Use strong passwords and rotate API tokens
4. **Performance**: Monitor memory usage and upgrade if needed

## 📞 Support

- **Firefly III Docs**: https://docs.firefly-iii.org/
- **Render Support**: https://render.com/docs
- **Community**: Firefly III Discord/GitHub

---

**Estimated Setup Time**: 30-45 minutes
**Monthly Cost**: $7-15 (Starter instances + database)
**Maintenance**: Minimal (auto-updates available)

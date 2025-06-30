# Firefly III Integration Setup Guide

This guide will help you set up Firefly III integration with the Phygital Facility Manager for comprehensive financial management.

## 🎯 **What is Firefly III?**

Firefly III is a powerful, open-source personal finance manager that helps you:
- Track income and expenses
- Manage budgets and categories
- Monitor account balances
- Generate financial reports
- Analyze spending patterns

## 🚀 **Recommended Setup with Docker Compose**

### **Step 1: Download Configuration Files**

Create a new directory for Firefly III and download the required files:

```bash
# Create directory
mkdir firefly-iii-setup
cd firefly-iii-setup

# Download Docker Compose file
curl -o docker-compose.yml https://raw.githubusercontent.com/firefly-iii/docker/main/docker-compose.yml

# Download environment files
curl -o .env https://raw.githubusercontent.com/firefly-iii/firefly-iii/main/.env.example
curl -o .db.env https://raw.githubusercontent.com/firefly-iii/docker/main/database.env
```

### **Step 2: Configure Environment Variables**

Edit the `.env` file and change the database password:
```bash
# Find this line and change the password
DB_PASSWORD=your_secure_password_here
```

Edit the `.db.env` file and set the SAME password:
```bash
# Change this to match the password in .env
MYSQL_PASSWORD=your_secure_password_here
```

### **Step 3: Start Firefly III**

```bash
# Start the containers
docker compose up -d --pull=always

# Follow the installation progress
docker compose logs -f
```

### **Step 4: Alternative - Quick Single Container Setup**

If you prefer a simpler setup with SQLite (no separate database):

```bash
# Generate a random 32-character key
APP_KEY=$(head /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c 32)

# Create volume for uploads
docker volume create firefly_iii_upload

# Run Firefly III with SQLite
docker run -d \
  --name firefly-iii \
  -p 8080:8080 \
  -e APP_KEY=$APP_KEY \
  -e DB_CONNECTION=sqlite \
  -e APP_URL=http://localhost:8080 \
  -v firefly_iii_upload:/var/www/html/storage/upload \
  fireflyiii/core:latest
```

### **Step 2: Initial Setup**

1. **Open Firefly III**: Navigate to `http://localhost:8080`
2. **Create Admin Account**: Follow the setup wizard to create your admin account
3. **Complete Initial Configuration**: Set up your default currency and basic settings

### **Step 3: Create Personal Access Token**

1. **Login to Firefly III**: Go to `http://localhost:8080`
2. **Navigate to Profile**: Click on your profile → "Profile"
3. **Go to OAuth Section**: Click on "OAuth" tab
4. **Create Personal Access Token**:
   - Click "Create new token"
   - Give it a name like "Facility Manager Integration"
   - Copy the generated token (it's very long!)

### **Step 4: Configure Environment Variables**

Update your `.env` file in the backend directory:

```env
# Firefly III Configuration
FIREFLY_BASE_URL=http://localhost:8080
FIREFLY_API_TOKEN=your_very_long_personal_access_token_here
```

### **Step 5: Restart the Application**

```bash
# Stop the backend
# Restart with new environment variables
cd phygital-facility-manager/backend
python app.py
```

## 🏗️ **Advanced Setup with Docker Compose**

For a more robust setup, create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  firefly-iii-db:
    image: postgres:13
    environment:
      POSTGRES_DB: firefly
      POSTGRES_USER: firefly
      POSTGRES_PASSWORD: secret_firefly_password
    volumes:
      - firefly_iii_db:/var/lib/postgresql/data

  firefly-iii:
    image: fireflyiii/core:latest
    depends_on:
      - firefly-iii-db
    ports:
      - "8080:8080"
    environment:
      APP_KEY: SomeRandomStringOf32CharsExactly
      DB_CONNECTION: pgsql
      DB_HOST: firefly-iii-db
      DB_PORT: 5432
      DB_DATABASE: firefly
      DB_USERNAME: firefly
      DB_PASSWORD: secret_firefly_password
      APP_URL: http://localhost:8080
      TRUSTED_PROXIES: "**"
    volumes:
      - firefly_iii_upload:/var/www/html/storage/upload

volumes:
  firefly_iii_db:
  firefly_iii_upload:
```

Run with: `docker-compose up -d`

## 📊 **Setting Up Your Financial Data**

### **1. Create Accounts**

In Firefly III, create accounts that represent your facility's finances:

- **Asset Accounts**: 
  - Maintenance Fund Account
  - Reserve Fund Account
  - Operating Account

- **Expense Accounts**:
  - Utilities
  - Maintenance & Repairs
  - Security Services
  - Cleaning Services
  - Administrative Expenses

- **Revenue Accounts**:
  - Maintenance Fees
  - Parking Fees
  - Amenity Charges

### **2. Set Up Categories**

Create categories for better organization:
- Building Maintenance
- Utilities (Electricity, Water, Gas)
- Security & Safety
- Landscaping & Gardening
- Administrative
- Insurance
- Legal & Professional Services

### **3. Create Budgets**

Set monthly/yearly budgets for:
- Regular maintenance
- Utility bills
- Security services
- Emergency repairs
- Administrative costs

## 🎛️ **Using the Financial Dashboard**

Once configured, the Financial Dashboard provides:

### **📈 Overview Cards**
- **Total Assets**: Sum of all asset accounts
- **Total Liabilities**: Sum of all liability accounts  
- **Net Worth**: Assets minus liabilities
- **Account Count**: Number of active accounts

### **📋 Tabs**
1. **Recent Transactions**: Latest financial activities
2. **Accounts**: All accounts with current balances
3. **Budgets**: Budget overview and status

### **🔗 Quick Actions**
- **Refresh Data**: Update dashboard with latest Firefly III data
- **Open Firefly III**: Direct link to full Firefly III interface

## 🔧 **API Endpoints Available**

The integration provides these API endpoints:

- `GET /api/firefly/test` - Test connection
- `GET /api/firefly/summary` - Financial summary
- `GET /api/firefly/accounts` - List accounts
- `GET /api/firefly/transactions` - List transactions
- `GET /api/firefly/budgets` - List budgets
- `GET /api/firefly/categories` - List categories
- `POST /api/firefly/transactions` - Create transaction
- `GET /api/firefly/reports/monthly` - Monthly report
- `GET /api/firefly/analytics/spending` - Spending analytics

## 🛠️ **Troubleshooting**

### **Connection Issues**
- Ensure Firefly III is running on port 8080
- Check that `FIREFLY_BASE_URL` is correct
- Verify the Personal Access Token is valid

### **Permission Issues**
- Make sure the Personal Access Token has proper permissions
- Check Firefly III logs: `docker logs firefly-iii`

### **Data Not Showing**
- Verify you have created accounts and transactions in Firefly III
- Check the browser console for JavaScript errors
- Test API endpoints directly: `curl http://localhost:5000/api/firefly/test`

## 📚 **Additional Resources**

- [Firefly III Documentation](https://docs.firefly-iii.org/)
- [Firefly III API Documentation](https://api-docs.firefly-iii.org/)
- [Docker Installation Guide](https://docs.firefly-iii.org/how-to/firefly-iii/installation/docker/)

## 🎉 **Benefits of Integration**

✅ **Comprehensive Financial Tracking**: Track all facility income and expenses
✅ **Budget Management**: Set and monitor budgets for different categories
✅ **Automated Reporting**: Generate monthly and yearly financial reports
✅ **Spending Analytics**: Analyze spending patterns and trends
✅ **Multi-Account Support**: Manage multiple accounts (maintenance fund, reserves, etc.)
✅ **Transaction Categorization**: Organize expenses by type and purpose
✅ **Real-time Dashboard**: Live financial overview in the facility manager
✅ **Professional Reports**: Generate reports for board meetings and audits

The Firefly III integration transforms your facility management system into a complete financial management solution!

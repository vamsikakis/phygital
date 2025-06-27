# Migration from Supabase to Neon PostgreSQL

This guide will help you migrate your Phygital Facility Manager application from Supabase to Neon PostgreSQL.

## 🎯 Overview

We've completely removed Supabase dependencies and replaced them with direct Neon PostgreSQL connections. This provides:

- ✅ Better performance and control
- ✅ Direct PostgreSQL access with pgvector for AI features
- ✅ Simplified architecture
- ✅ Cost-effective scaling
- ✅ Enhanced vector search capabilities

## 📋 Prerequisites

1. **Neon PostgreSQL Account**: Sign up at [neon.tech](https://neon.tech)
2. **Python 3.8+**: Ensure you have Python installed
3. **Node.js 16+**: For the frontend application

## 🚀 Step-by-Step Migration

### 1. Create Neon Database

1. Go to [Neon Console](https://console.neon.tech)
2. Create a new project
3. Note down your connection details:
   - Host (e.g., `ep-xxx.us-east-1.aws.neon.tech`)
   - Database name
   - Username
   - Password

### 2. Install pgvector Extension (Optional but Recommended)

For AI-powered document search, install the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Update Environment Configuration

Copy the example environment file and update it:

```bash
cd backend
cp .env.example .env
```

Update your `.env` file with Neon credentials:

```env
# Neon PostgreSQL Database Configuration
DB_HOST=your-neon-hostname.neon.tech
DB_NAME=your-database-name
DB_USER=your-username
DB_PASSWORD=your-password
DB_PORT=5432

# OpenAI API key (required for AI features)
OPENAI_API_KEY=your-openai-api-key

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_EXPIRATION=86400

# Storage Configuration
STORAGE_ROOT=./storage
```

### 4. Install Dependencies

Install the updated Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 5. Test Database Connection

Run the connection test script:

```bash
cd backend
python test_neon_connection.py
```

This will:
- ✅ Test database connectivity
- ✅ Create all necessary tables
- ✅ Test basic CRUD operations
- ✅ Test vector operations (if pgvector is installed)

### 6. Initialize Database

If the test passes, your database is ready! The script automatically creates all tables.

### 7. Start the Application

```bash
# Backend
cd backend
python app.py

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

## 🔄 Data Migration (If Needed)

If you have existing data in Supabase, you can migrate it:

### Export from Supabase

1. Go to your Supabase dashboard
2. Navigate to SQL Editor
3. Export your data using SQL queries:

```sql
-- Export users
SELECT * FROM users;

-- Export documents
SELECT * FROM documents;

-- Export other tables as needed
```

### Import to Neon

1. Use the exported data to create INSERT statements
2. Run them in your Neon database console or via psql

## 🏗️ Architecture Changes

### What Changed

1. **Database Layer**: 
   - ❌ Removed: Supabase client
   - ✅ Added: Direct PostgreSQL with SQLAlchemy

2. **Storage Layer**:
   - ❌ Removed: Supabase Storage
   - ✅ Added: Local file storage system

3. **Authentication**:
   - ❌ Removed: Supabase Auth
   - ✅ Added: JWT-based authentication

4. **Vector Search**:
   - ❌ Removed: External vector services
   - ✅ Added: PostgreSQL with pgvector extension

### File Structure Changes

```
backend/
├── database.py          # New: Direct PostgreSQL models
├── db.py                # Updated: Backward compatibility wrapper
├── integrations/
│   ├── local_storage.py # New: Local file storage
│   └── storage.py       # Updated: Compatibility wrapper
├── test_neon_connection.py  # New: Connection test script
└── .env.example         # Updated: Neon configuration
```

## 🔧 Configuration Options

### Vector Search Configuration

```env
# Vector Database Configuration
VECTOR_DIMENSION=1536
VECTOR_MODEL=text-embedding-3-small
```

### File Storage Configuration

```env
# Storage Configuration
STORAGE_ROOT=./storage
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,txt,doc,docx,png,jpg,jpeg,gif
```

### Security Configuration

```env
# JWT Configuration
JWT_SECRET_KEY=your-secure-secret-key
JWT_EXPIRATION=86400  # 24 hours

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🧪 Testing

### Run All Tests

```bash
cd backend
python test_neon_connection.py
python test_enhanced_upload.py  # Test document upload with vector storage
```

### Manual Testing

1. **Database Connection**: Check if tables are created
2. **File Upload**: Upload a document via the web interface
3. **AI Search**: Test semantic search functionality
4. **Authentication**: Test user login/registration

## 🚨 Troubleshooting

### Common Issues

1. **Connection Failed**
   ```
   Error: connection to server failed
   ```
   - Check your Neon credentials in `.env`
   - Ensure your IP is whitelisted in Neon console

2. **pgvector Extension Missing**
   ```
   Error: extension "vector" does not exist
   ```
   - Install pgvector extension in Neon console
   - Or disable vector features temporarily

3. **File Upload Issues**
   ```
   Error: Permission denied
   ```
   - Check storage folder permissions
   - Ensure `STORAGE_ROOT` directory exists

### Getting Help

1. Check the logs in `./logs/app.log`
2. Run the test scripts for detailed error messages
3. Verify all environment variables are set correctly

## 🎉 Benefits of Migration

1. **Performance**: Direct database access is faster
2. **Cost**: Neon's pricing is more predictable
3. **Control**: Full control over your database
4. **Scalability**: Better scaling options
5. **AI Features**: Enhanced vector search with pgvector

## 📚 Additional Resources

- [Neon Documentation](https://neon.tech/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Migration Complete!** 🎊

Your application is now running on Neon PostgreSQL with enhanced AI capabilities and better performance.

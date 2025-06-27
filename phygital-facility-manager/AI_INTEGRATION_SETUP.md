# AI Integration Setup Guide

## Overview
This guide walks you through setting up the AI integration for the Gopalan Atlantis Facility Management System. The integration includes OpenAI GPT-4, embeddings, vector search, and PostgreSQL with pgvector.

## Prerequisites

### 1. OpenAI API Key
- Sign up at [OpenAI Platform](https://platform.openai.com/)
- Create an API key with access to:
  - GPT-4 (for chat completions)
  - text-embedding-3-small (for embeddings)
- Add credits to your account

### 2. PostgreSQL Database with pgvector
We recommend using **Neon** (neon.tech) for managed PostgreSQL with pgvector:

1. Sign up at [Neon](https://neon.tech/)
2. Create a new project
3. Enable the pgvector extension in your database
4. Get your connection string

## Environment Setup

### 1. Create Environment File
Create a `.env` file in the `backend` directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (Neon PostgreSQL)
DB_HOST=your_neon_host
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432

# Optional: Assistant Configuration
OPENAI_ASSISTANT_ID=your_assistant_id_here
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- openai>=1.0.0
- psycopg2-binary
- numpy
- python-dotenv

## Database Setup

### 1. Automatic Setup (Recommended)
Run the setup script to automatically configure your database:

```bash
cd backend
python setup_database.py
```

This script will:
- Create the database if it doesn't exist
- Install pgvector extension
- Create required tables
- Set up indexes for vector search
- Insert sample data

### 2. Manual Setup (Alternative)
If you prefer manual setup, run these SQL commands:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create document embeddings table
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create vector similarity index
CREATE INDEX idx_document_embeddings_embedding 
ON document_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create assistant threads table
CREATE TABLE assistant_threads (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create query logs table
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255),
    query TEXT NOT NULL,
    response TEXT,
    module VARCHAR(50),
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);
```

## Testing the Setup

### 1. Quick Test
Run the simple test to verify basic connectivity:

```bash
cd backend
python simple_ai_test.py
```

### 2. Comprehensive Test
Run the full integration test suite:

```bash
cd backend
python test_ai_integration.py
```

This will test:
- Environment variables
- Database connectivity
- pgvector extension
- OpenAI API connectivity
- Vector service functionality
- Assistant service
- Complete integration flow

## OpenAI Assistant Setup (Optional)

### 1. Create Assistant via API
```python
import openai

client = openai.OpenAI(api_key="your_api_key")

assistant = client.beta.assistants.create(
    name="Gopalan Atlantis Assistant",
    instructions="""You are a helpful assistant for Gopalan Atlantis apartment residents. 
    You help with facility information, amenities, rules, and general inquiries.""",
    model="gpt-4",
    tools=[{"type": "retrieval"}]
)

print(f"Assistant ID: {assistant.id}")
```

### 2. Add Assistant ID to Environment
Add the assistant ID to your `.env` file:
```
OPENAI_ASSISTANT_ID=asst_your_assistant_id_here
```

## API Endpoints

Once setup is complete, these endpoints will be available:

### AI Query
```
POST /api/query
Content-Type: application/json

{
    "query": "What are the pool timings?"
}
```

### Assistant Chat
```
POST /api/assistant/threads
GET /api/assistant/init
POST /api/assistant/threads/{thread_id}/messages
```

### Document Management
```
POST /api/akc/documents
GET /api/akc/documents
```

## Features

### 1. Semantic Search
- Upload documents and they're automatically embedded
- Search using natural language queries
- Vector similarity matching with pgvector

### 2. AI Assistant
- Conversational AI for residents
- Context-aware responses
- Thread-based conversations

### 3. Intelligent Routing
- Queries automatically routed to appropriate modules:
  - AKC (Apartment Knowledge Center)
  - OCE (Online Communication Engine)
  - HDC (Help Desk Center)

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Verify your API key is correct
   - Check you have sufficient credits
   - Ensure you have access to GPT-4 and embeddings

2. **Database Connection Error**
   - Verify your database credentials
   - Check if pgvector extension is installed
   - Ensure your IP is whitelisted (for cloud databases)

3. **Vector Search Not Working**
   - Verify pgvector extension is installed
   - Check if the vector index was created
   - Ensure embeddings table has data

### Debug Mode
Run the application in debug mode for detailed logs:

```bash
cd backend
FLASK_DEBUG=1 python app.py
```

## Security Notes

1. **Never commit your `.env` file** - it's already in `.gitignore`
2. **Use environment variables** for all sensitive data
3. **Rotate API keys regularly**
4. **Use database connection pooling** in production

## Next Steps

1. **Upload Documents**: Use the document upload feature to add facility information
2. **Test Queries**: Try various natural language queries
3. **Customize Assistant**: Modify the assistant instructions for your specific needs
4. **Monitor Usage**: Check OpenAI usage dashboard for API consumption

## Support

For issues or questions:
1. Check the test outputs for specific error messages
2. Review the Flask application logs
3. Verify all environment variables are set correctly
4. Ensure database connectivity and pgvector extension

The AI integration provides powerful semantic search and conversational AI capabilities for your apartment management system!

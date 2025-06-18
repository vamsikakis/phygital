# Migration from Weaviate to OpenAI Vector Store

This document outlines the migration process from Weaviate to OpenAI Vector Store for the Phygital Facility Manager application.

## Migration Overview

The migration involves replacing the Weaviate-based RAG system with OpenAI's Vector Store and Assistant API. This provides several benefits:

1. Simplified architecture with direct integration to OpenAI's ecosystem
2. Improved retrieval quality with OpenAI's vector embeddings
3. Access to OpenAI's Assistant API features
4. Reduced infrastructure maintenance

## Migration Components

### Backend

1. **OpenAI Assistant Service**
   - Created `openai_assistant_service.py` for managing:
     - Assistant initialization and retrieval
     - Thread and message management
     - Running the assistant
     - File upload, listing, and deletion

2. **API Routes**
   - Added `assistant_routes.py` with endpoints for:
     - Assistant initialization
     - Thread management
     - Message handling
     - File operations

3. **Migration Service**
   - Created `migration_service.py` to facilitate migration from Weaviate
   - Added migration routes in `migration_routes.py`

### Frontend

1. **OpenAI Assistant Components**
   - `OpenAIChatView.tsx`: Chat interface for AI assistant conversations
   - `OpenAIDocumentsView.tsx`: Document management interface
   - `OpenAIDocumentAssistant.tsx`: Combined tabbed interface

2. **Services and Hooks**
   - `openaiAssistantService.ts`: Service for interacting with backend API
   - `useOpenAIAssistant.ts`: React hook for assistant functionality

3. **Migration Dashboard**
   - Added `MigrationDashboard.tsx` for monitoring and managing migration

## Migration Steps

### Phase 1: Setup and Configuration

1. Install required dependencies
   ```bash
   pip install openai
   ```

2. Configure environment variables
   ```
   OPENAI_API_KEY=your_api_key
   OPENAI_ASSISTANT_ID=your_assistant_id (optional, will be created if not provided)
   ```

### Phase 2: Data Migration

1. Use the Migration Dashboard to migrate documents from Weaviate to OpenAI
2. Verify document counts match between systems
3. Test retrieval quality with sample queries

### Phase 3: Code Cleanup

1. Run the cleanup script to identify Weaviate references
   ```bash
   python backend/scripts/cleanup_weaviate.py
   ```

2. Remove Weaviate-related code and dependencies
   ```bash
   python backend/scripts/cleanup_weaviate.py --remove
   ```

3. Update any remaining references manually

### Phase 4: Testing and Validation

1. Test all AI assistant functionality
2. Verify document retrieval works correctly
3. Check that document upload and management functions properly

## Rollback Plan

If issues are encountered during migration:

1. Keep both systems running in parallel during initial deployment
2. Maintain Weaviate backups until migration is fully validated
3. Use feature flags to control which system is active

## Post-Migration Tasks

1. Remove Weaviate infrastructure
2. Update documentation
3. Train users on new interface

## Migration Status

- [x] Backend OpenAI Assistant Service
- [x] Backend Assistant Routes
- [x] Frontend OpenAI Assistant Components
- [x] Migration Service and Dashboard
- [ ] Data Migration
- [ ] Code Cleanup
- [ ] Testing and Validation

#!/usr/bin/env python3
"""Test import of document routes"""

try:
    from routes.document_routes import documents_bp
    print("✅ Document routes imported successfully")
    print(f"Blueprint name: {documents_bp.name}")
except Exception as e:
    print(f"❌ Error importing document routes: {e}")
    import traceback
    traceback.print_exc()

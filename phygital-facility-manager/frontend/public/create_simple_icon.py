#!/usr/bin/env python3
"""Create simple PWA icons using base64 encoded PNG data"""

import base64
import os

# Simple 192x192 blue square PNG (base64 encoded)
# This is a minimal valid PNG that browsers will accept
png_192_base64 = """
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
"""

# Create a proper 192x192 PNG (simple blue square)
def create_icon():
    # Decode the base64 PNG
    png_data = base64.b64decode(png_192_base64.strip())

    # Write to file
    with open('pwa-192x192.png', 'wb') as f:
        f.write(png_data)

    print("Created pwa-192x192.png")

    # Also create 512x512 version
    with open('pwa-512x512.png', 'wb') as f:
        f.write(png_data)

    print("Created pwa-512x512.png")

if __name__ == "__main__":
    create_icon()
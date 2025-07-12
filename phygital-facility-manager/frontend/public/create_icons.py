#!/usr/bin/env python3
"""Create proper PWA icons using PIL"""

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_icon_with_pil(size, color=(63, 81, 181)):
    """Create an icon using PIL"""
    # Create a new image with the specified size
    img = Image.new('RGBA', (size, size), color + (255,))
    
    # Add a simple design - a circle with border
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=color + (255,), outline=(255, 255, 255, 255), width=size//32)
    
    # Add a smaller inner circle
    inner_margin = size // 4
    inner_color = tuple(min(255, c + 50) for c in color)
    draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                fill=inner_color + (255,))
    
    return img

def create_simple_icon(size, color=(63, 81, 181)):
    """Create a simple solid color icon without PIL"""
    import struct
    import zlib
    
    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk data
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)  # RGBA format
    
    # Create image data (solid color)
    image_data = b''
    for y in range(size):
        row_data = b'\x00'  # Filter type 0 (None)
        for x in range(size):
            image_data += bytes(color) + b'\xff'  # RGBA pixel
    
    # Compress image data
    compressed_data = zlib.compress(image_data)
    
    # Calculate CRCs
    ihdr_chunk = b'IHDR' + ihdr_data
    idat_chunk = b'IDAT' + compressed_data
    iend_chunk = b'IEND'
    
    ihdr_crc = zlib.crc32(ihdr_chunk) & 0xffffffff
    idat_crc = zlib.crc32(idat_chunk) & 0xffffffff
    iend_crc = zlib.crc32(iend_chunk) & 0xffffffff
    
    # Assemble PNG
    png_data = png_signature
    png_data += struct.pack('>I', len(ihdr_data)) + ihdr_chunk + struct.pack('>I', ihdr_crc)
    png_data += struct.pack('>I', len(compressed_data)) + idat_chunk + struct.pack('>I', idat_crc)
    png_data += struct.pack('>I', 0) + iend_chunk + struct.pack('>I', iend_crc)
    
    return png_data

def create_icons():
    """Create PWA icons"""
    print("Creating PWA icons...")
    
    if PIL_AVAILABLE:
        print("Using PIL for high-quality icons...")
        
        # Create 192x192 icon
        img_192 = create_icon_with_pil(192)
        img_192.save('pwa-192x192.png', 'PNG')
        print("Created pwa-192x192.png (192x192)")
        
        # Create 512x512 icon
        img_512 = create_icon_with_pil(512)
        img_512.save('pwa-512x512.png', 'PNG')
        print("Created pwa-512x512.png (512x512)")
        
        # Create favicon
        img_32 = create_icon_with_pil(32)
        img_32.save('favicon.ico', 'ICO')
        print("Created favicon.ico (32x32)")
        
    else:
        print("PIL not available, creating simple icons...")
        
        # Create 192x192 icon
        icon_192 = create_simple_icon(192)
        with open('pwa-192x192.png', 'wb') as f:
            f.write(icon_192)
        print("Created pwa-192x192.png (192x192)")
        
        # Create 512x512 icon
        icon_512 = create_simple_icon(512)
        with open('pwa-512x512.png', 'wb') as f:
            f.write(icon_512)
        print("Created pwa-512x512.png (512x512)")
        
        print("Note: Install Pillow (pip install Pillow) for better quality icons")

if __name__ == "__main__":
    create_icons()

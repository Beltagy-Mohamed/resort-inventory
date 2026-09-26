import os
from PIL import Image

logo_path = r"C:\Users\belta\.gemini\antigravity\brain\8e892fad-5c1b-4a76-9e2b-8f2a1e88317b\.user_uploaded\media_1790242105236.jpg"
out_dir = r"g:\client_delivery\static\pwa\icons"
splash_dir = r"g:\client_delivery\static\pwa\splash"

os.makedirs(out_dir, exist_ok=True)
os.makedirs(splash_dir, exist_ok=True)

sizes = [72, 96, 128, 144, 152, 167, 180, 192, 384, 512]

with Image.open(logo_path) as img:
    # Ensure it's RGBA
    img = img.convert("RGBA")
    
    # Make a squared version for icons (add white padding if not square)
    w, h = img.size
    max_dim = max(w, h)
    square_img = Image.new("RGBA", (max_dim, max_dim), (255, 255, 255, 255))
    offset = ((max_dim - w) // 2, (max_dim - h) // 2)
    square_img.paste(img, offset, mask=img)
    
    for s in sizes:
        resized = square_img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(os.path.join(out_dir, f"icon-{s}.png"), format="PNG")
        
        # Maskable (same for now, ideally with padding, but our square_img has padding)
        if s in [192, 512]:
            # Add 20% extra padding for maskable
            maskable_size = int(s * 1.25)
            maskable_img = Image.new("RGBA", (maskable_size, maskable_size), (255, 255, 255, 255))
            moffset = ((maskable_size - s) // 2, (maskable_size - s) // 2)
            maskable_img.paste(resized, moffset, mask=resized)
            maskable_img = maskable_img.resize((s, s), Image.Resampling.LANCZOS)
            maskable_img.save(os.path.join(out_dir, f"icon-{s}-maskable.png"), format="PNG")
            
    # Create Shortcut Icons
    shortcut_scan = square_img.resize((96, 96), Image.Resampling.LANCZOS)
    shortcut_scan.save(os.path.join(out_dir, "shortcut-scan.png"), format="PNG")
    shortcut_scan.save(os.path.join(out_dir, "shortcut-transaction.png"), format="PNG")
    
    # Create Splash Screens (Background dark blue #0F172A, logo in center)
    splash_sizes = [
        (1170, 2532), # iPhone 12/13/14 Pro
        (1284, 2778), # iPhone 12/13/14 Pro Max
        (1125, 2436), # iPhone X/XS/11 Pro
        (828, 1792),  # iPhone XR/11
    ]
    
    for sw, sh in splash_sizes:
        splash = Image.new("RGBA", (sw, sh), (15, 23, 42, 255)) # #0F172A
        # Logo in center, scaled to 30% of width
        logo_w = int(sw * 0.3)
        logo_h = int((logo_w / w) * h)
        splash_logo = img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        offset = ((sw - logo_w) // 2, (sh - logo_h) // 2)
        splash.paste(splash_logo, offset, mask=splash_logo)
        
        splash.save(os.path.join(splash_dir, f"splash-{sw}x{sh}.png"), format="PNG")

print("PWA Icons and Splash screens generated.")

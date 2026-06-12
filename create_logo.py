"""
AiPlanner Logo Generator
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(output_path="logo.png", size=512):
    """
    AiPlanner logo yaratish
    """
    # Canvas yaratish
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Gradient background (ko'kdan binafshaga)
    for y in range(size):
        # Gradient hisoblash
        r = int(75 + (138 - 75) * y / size)   # 75 -> 138
        g = int(111 + (43 - 111) * y / size)  # 111 -> 43
        b = int(255 + (226 - 255) * y / size) # 255 -> 226
        draw.rectangle([0, y, size, y+1], fill=(r, g, b))
    
    # Doira (AI brain)
    circle_radius = size // 3
    circle_center = (size // 2, size // 2 - 30)
    
    # Tashqi doira (oq)
    draw.ellipse(
        [circle_center[0] - circle_radius, circle_center[1] - circle_radius,
         circle_center[0] + circle_radius, circle_center[1] + circle_radius],
        fill='white',
        outline='#4B6FFF',
        width=8
    )
    
    # AI brain chiziqlar
    brain_lines = [
        # Gorizontal chiziqlar
        [(circle_center[0] - 60, circle_center[1] - 40), 
         (circle_center[0] + 60, circle_center[1] - 40)],
        [(circle_center[0] - 70, circle_center[1]), 
         (circle_center[0] + 70, circle_center[1])],
        [(circle_center[0] - 60, circle_center[1] + 40), 
         (circle_center[0] + 60, circle_center[1] + 40)],
        
        # Vertikal chiziqlar
        [(circle_center[0] - 40, circle_center[1] - 60), 
         (circle_center[0] - 40, circle_center[1] + 60)],
        [(circle_center[0], circle_center[1] - 70), 
         (circle_center[0], circle_center[1] + 70)],
        [(circle_center[0] + 40, circle_center[1] - 60), 
         (circle_center[0] + 40, circle_center[1] + 60)],
    ]
    
    for line in brain_lines:
        draw.line(line, fill='#4B6FFF', width=5)
    
    # Nuqtalar (nodes)
    node_positions = [
        (circle_center[0] - 60, circle_center[1] - 40),
        (circle_center[0], circle_center[1] - 70),
        (circle_center[0] + 60, circle_center[1] - 40),
        (circle_center[0] - 70, circle_center[1]),
        (circle_center[0], circle_center[1]),
        (circle_center[0] + 70, circle_center[1]),
        (circle_center[0] - 60, circle_center[1] + 40),
        (circle_center[0], circle_center[1] + 70),
        (circle_center[0] + 60, circle_center[1] + 40),
    ]
    
    for pos in node_positions:
        draw.ellipse([pos[0]-8, pos[1]-8, pos[0]+8, pos[1]+8], 
                     fill='#FF6B9D', outline='white', width=2)
    
    # Checkmark (tasdiqlash belgisi)
    check_size = 40
    check_x = size // 2 + circle_radius - 30
    check_y = circle_center[1] + circle_radius - 30
    
    # Checkmark background
    draw.ellipse([check_x - check_size, check_y - check_size,
                  check_x + check_size, check_y + check_size],
                 fill='#00D084', outline='white', width=4)
    
    # Checkmark symbol
    check_points = [
        (check_x - 15, check_y),
        (check_x - 5, check_y + 15),
        (check_x + 15, check_y - 15)
    ]
    draw.line(check_points[:2], fill='white', width=6)
    draw.line(check_points[1:], fill='white', width=6)
    
    # Matn (AiPlanner)
    try:
        # Font o'lchami
        font_size = size // 8
        # Default font ishlatamiz (PIL bilan birga keladi)
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = None
    
    text = "AiPlanner"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size - text_width) // 2
    text_y = size - text_height - 40
    
    # Text shadow
    draw.text((text_x + 2, text_y + 2), text, fill='#00000040', font=font)
    # Main text
    draw.text((text_x, text_y), text, fill='white', font=font)
    
    # Saqlash
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Logo yaratildi: {output_path}")
    return output_path

if __name__ == "__main__":
    # Turli o'lchamlarda yaratish
    create_logo("logo_512.png", 512)    # Telegram bot uchun
    create_logo("logo_1024.png", 1024)  # Yuqori sifat
    print("\n🎉 Logolar tayyor!")
    print("📁 Fayllar:")
    print("  - logo_512.png (Telegram bot)")
    print("  - logo_1024.png (Yuqori sifat)")

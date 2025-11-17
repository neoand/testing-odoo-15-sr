#!/usr/bin/env python3
"""
Create professional 128x128 PNG icon for Odoo 15 SMS Advanced module
Based on Odoo requirements from GitHub issues and documentation
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create 128x128 image with transparent background
size = 128
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Define colors - Modern green gradient theme
bg_color1 = (76, 175, 80)      # #4CAF50 - Material Green
bg_color2 = (46, 125, 50)      # #2E7D32 - Dark Green
message_color = (255, 255, 255)  # White
accent_color = (255, 152, 0)   # #FF9800 - Orange

# Draw rounded rectangle background with gradient effect
# We'll simulate gradient by drawing multiple rectangles
for i in range(size):
    # Calculate gradient color
    ratio = i / size
    r = int(bg_color1[0] * (1 - ratio) + bg_color2[0] * ratio)
    g = int(bg_color1[1] * (1 - ratio) + bg_color2[1] * ratio)
    b = int(bg_color1[2] * (1 - ratio) + bg_color2[2] * ratio)
    draw.rectangle([(0, i), (size, i+1)], fill=(r, g, b, 255))

# Draw rounded corners by overlaying transparent corners
corner_radius = 16
# Top-left corner
draw.rectangle([(0, 0), (corner_radius, corner_radius)], fill=(0, 0, 0, 0))
draw.pieslice([(0, 0), (corner_radius*2, corner_radius*2)], 180, 270, fill=bg_color1)

# Top-right corner
draw.rectangle([(size-corner_radius, 0), (size, corner_radius)], fill=(0, 0, 0, 0))
draw.pieslice([(size-corner_radius*2, 0), (size, corner_radius*2)], 270, 360, fill=bg_color1)

# Bottom-left corner
draw.rectangle([(0, size-corner_radius), (corner_radius, size)], fill=(0, 0, 0, 0))
draw.pieslice([(0, size-corner_radius*2), (corner_radius*2, size)], 90, 180, fill=bg_color2)

# Bottom-right corner
draw.rectangle([(size-corner_radius, size-corner_radius), (size, size)], fill=(0, 0, 0, 0))
draw.pieslice([(size-corner_radius*2, size-corner_radius*2), (size, size)], 0, 90, fill=bg_color2)

# Draw chat bubble (main SMS icon)
bubble_margin = 24
bubble_width = size - bubble_margin * 2
bubble_height = 50
bubble_x = bubble_margin
bubble_y = bubble_margin + 5

# Draw bubble shadow for depth
shadow_offset = 2
draw.rounded_rectangle(
    [(bubble_x + shadow_offset, bubble_y + shadow_offset),
     (bubble_x + bubble_width + shadow_offset, bubble_y + bubble_height + shadow_offset)],
    radius=8,
    fill=(0, 0, 0, 50)
)

# Draw main bubble
draw.rounded_rectangle(
    [(bubble_x, bubble_y), (bubble_x + bubble_width, bubble_y + bubble_height)],
    radius=8,
    fill=message_color
)

# Draw bubble tail (small triangle)
tail_points = [
    (bubble_x + 15, bubble_y + bubble_height),
    (bubble_x + 10, bubble_y + bubble_height + 8),
    (bubble_x + 20, bubble_y + bubble_height)
]
draw.polygon(tail_points, fill=message_color)

# Draw message lines inside bubble
line_margin = 10
line_width_1 = 40
line_width_2 = 55
line_width_3 = 35
line_height = 3
line_spacing = 8

# Line 1
draw.rounded_rectangle(
    [(bubble_x + line_margin, bubble_y + 12),
     (bubble_x + line_margin + line_width_1, bubble_y + 12 + line_height)],
    radius=2,
    fill=bg_color1
)

# Line 2
draw.rounded_rectangle(
    [(bubble_x + line_margin, bubble_y + 12 + line_spacing),
     (bubble_x + line_margin + line_width_2, bubble_y + 12 + line_spacing + line_height)],
    radius=2,
    fill=(129, 199, 132)  # Lighter green
)

# Line 3
draw.rounded_rectangle(
    [(bubble_x + line_margin, bubble_y + 12 + line_spacing * 2),
     (bubble_x + line_margin + line_width_3, bubble_y + 12 + line_spacing * 2 + line_height)],
    radius=2,
    fill=(165, 214, 167)  # Even lighter green
)

# Draw "send" icon (paper plane) in bottom right
plane_size = 28
plane_x = size - bubble_margin - plane_size - 5
plane_y = size - bubble_margin - plane_size

# Draw circle background for plane
draw.ellipse(
    [(plane_x - 4, plane_y - 4), (plane_x + plane_size + 4, plane_y + plane_size + 4)],
    fill=accent_color
)

# Draw simplified paper plane shape
plane_points = [
    (plane_x + 6, plane_y + 14),
    (plane_x + 22, plane_y + 8),
    (plane_x + 22, plane_y + 20),
    (plane_x + 6, plane_y + 14)
]
draw.polygon(plane_points, fill=message_color)

# Plane wing
wing_points = [
    (plane_x + 22, plane_y + 8),
    (plane_x + 26, plane_y + 12),
    (plane_x + 22, plane_y + 20)
]
draw.polygon(wing_points, fill=(255, 255, 255, 200))

# Save as PNG
output_path = '/Users/andersongoliveira/odoo_15_sr/chatroom_sms_advanced/static/description/icon.png'
img.save(output_path, 'PNG', optimize=True)
print(f"✅ Professional icon created: {output_path}")
print(f"   Size: 128x128 pixels")
print(f"   Format: PNG with transparency")
print(f"   File size: {os.path.getsize(output_path)} bytes")

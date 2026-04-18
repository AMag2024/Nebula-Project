import numpy as np
import hashlib
from PIL import Image, ImageDraw, ImageFilter

# ------- Helper Functions -------
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def heat_to_rgb(heat, palette):
    """
    heat = 1.0 → hot color (core)
    heat = 0.5 → mid color (main nebula)
    heat = 0.0 → cold color (outer edges)
    """
    hot  = [c / 255 for c in hex_to_rgb(palette["hot"])]
    mid  = [c / 255 for c in hex_to_rgb(palette["mid"])]
    cold = [c / 255 for c in hex_to_rgb(palette["cold"])]

    if heat > 0.5:
        t = (heat - 0.5) * 2
        rgb = [int((mid[i] + t * (hot[i] - mid[i])) * 255) for i in range(3)]
    else:
        t = heat * 2
        rgb = [int((cold[i] + t * (mid[i] - cold[i])) * 255) for i in range(3)]

    return tuple(np.clip(rgb, 0, 255))

def add_layers(base, layer):
    base_arr  = np.array(base,  dtype=np.float32)
    layer_arr = np.array(layer, dtype=np.float32)
    # screen blending instead of additive — resists blowing out to white
    blended = 255 - (255 - base_arr) * (255 - layer_arr) / 255
    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), "RGBA")

def draw_soft_blob(size, color, alpha, blur_radius):
    """Draw a single soft glowing blob on its own layer then blur it."""
    pad    = int(blur_radius * 3)
    canvas = size + pad * 2
    layer  = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(layer)
    r, g, b = color
    draw.ellipse([pad, pad, pad + size, pad + size], fill=(r, g, b, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return layer, pad

def stamp_blob(image, blob_layer, cx, cy, pad):
    """Stamp a blob layer onto the main image at the right position."""
    x = int(cx - pad - (blob_layer.width  - pad * 2) / 2)
    y = int(cy - pad - (blob_layer.height - pad * 2) / 2)
    return add_layers(image, Image.new("RGBA", image.size, (0,0,0,0)).__class__.paste
                      if False else _stamp(image, blob_layer, x, y))

def _stamp(base, layer, x, y):
    """Paste a layer onto a base image using additive blending."""
    temp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    temp.paste(layer, (x, y))
    return add_layers(base, temp)

def turbulent_warp(x, y, strength, rng, seed_offset=0):
    """
    Displaces a point using layered sine waves to simulate
    turbulent gas motion. Higher strength = more chaotic edges.
    """
    # multiple sine waves at different frequencies and angles
    # layering them creates an irregular non-repeating pattern
    warp_x  = strength * (
        0.5 * np.sin(y * 8.3 + seed_offset) +
        0.3 * np.sin(x * 13.1 + y * 5.7 + seed_offset * 1.3) +
        0.2 * np.sin(x * 6.2 - y * 11.4 + seed_offset * 0.7)
    )
    warp_y  = strength * (
        0.5 * np.cos(x * 7.6 + seed_offset) +
        0.3 * np.cos(y * 12.3 - x * 4.8 + seed_offset * 1.1) +
        0.2 * np.cos(x * 9.1 + y * 8.5 + seed_offset * 0.9)
    )
    return x + warp_x, y + warp_y

# ------- User Input -------
user_input    = input("Enter a seed phrase or number: ")
print("\nCustomize your nebula (press Enter to use defaults):")
density_input = input("Density    — low / medium / high       (default: medium): ").strip().lower()
spread_input  = input("Spread     — tight / normal / wide     (default: normal): ").strip().lower()
color_input   = input("Color theme— pink / fire / blue / green (default: auto):  ").strip().lower()

# ------- Seed -------
hash_bytes = hashlib.md5(user_input.encode()).hexdigest()
seed       = int(hash_bytes, 16) % (2**32)
print(f"\nSeed: {seed}")
rng = np.random.default_rng(seed)

# ------- Settings -------
density_map = {"low": 0.6, "medium": 1.0, "high": 2.0}
spread_map  = {"tight": 0.08, "normal": 0.18, "wide": 0.30}
color_map   = {"pink": 0, "fire": 1, "blue": 2, "green": 3}

density = density_map.get(density_input, 1.0)
spread  = spread_map.get(spread_input,  0.18)

palette_options = [
    {"hot": "#ffffff", "mid": "#c084fc", "cold": "#1e0a3c"},  # purple
    {"hot": "#ffffff", "mid": "#ef4444", "cold": "#1a0500"},  # fire
    {"hot": "#ffffff", "mid": "#22d3ee", "cold": "#020d1a"},  # blue
    {"hot": "#ffffff", "mid": "#4ade80", "cold": "#011a08"},  # green
]
palette = palette_options[color_map[color_input]] if color_input in color_map \
          else palette_options[seed % len(palette_options)]

# ------- Canvas -------
W, H   = 1000, 1000
image  = Image.new("RGBA", (W, H), (0, 0, 0, 255))

# pixel helper — converts 0-1 coords to pixel coords
def px(v): return int(v * W)
def py(v): return int(v * H)

# ------- Stars -------
NUM_STARS = int(1200 * density)
for _ in range(NUM_STARS):
    sx     = rng.uniform(0, W)
    sy     = rng.uniform(0, H)
    radius = rng.uniform(0.3, 1.8)
    bright = int(rng.uniform(80, 255))

    star_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw       = ImageDraw.Draw(star_layer)
    draw.ellipse(
        [sx - radius, sy - radius, sx + radius, sy + radius],
        fill=(bright, bright, bright, bright)
    )
    image = add_layers(image, star_layer)

# ------- Cluster Setup -------
NUM_CLUSTERS    = int(rng.integers(3, 7))
cluster_x       = rng.uniform(0.2, 0.8, size=NUM_CLUSTERS)
cluster_y       = rng.uniform(0.2, 0.8, size=NUM_CLUSTERS)
cluster_spread_x = rng.uniform(0.2, 0.5, size=NUM_CLUSTERS)  
cluster_spread_y = rng.uniform(0.2, 0.5, size=NUM_CLUSTERS)
cluster_angle   = rng.uniform(0, np.pi, size=NUM_CLUSTERS)

print(f"Generating {NUM_CLUSTERS} clusters...")

# ------- Glowing Cores -------
for i in range(NUM_CLUSTERS):
    cx = px(cluster_x[i])
    cy = py(cluster_y[i])
    for blob_size, alpha, blur in [
        (300, 3,  80),
        (180, 6,  50),
        (80,  12, 25),
        (30,  25, 10),
    ]:
        blob, pad = draw_soft_blob(blob_size, (255, 255, 255), alpha, blur)
        image = _stamp(image, blob, cx - blob_size // 2, cy - blob_size // 2)

# ------- Blob Generation -------
NUM_BLOBS        = int(200 * density)
blobs_per_cluster = NUM_BLOBS // NUM_CLUSTERS

print(f"Painting {NUM_BLOBS} nebula blobs...")

for i in range(NUM_CLUSTERS):
    cx_f = cluster_x[i]
    cy_f = cluster_y[i]
    sx   = cluster_spread_x[i]
    sy   = cluster_spread_y[i]
    ang  = cluster_angle[i]

    for _ in range(blobs_per_cluster):
        dist_scale = rng.power(0.95)

        raw_x = rng.normal(0, sx * dist_scale)
        raw_y = rng.normal(0, sy * dist_scale)

        # Step 1 — rotation (use blob_x/blob_y consistently throughout)
        blob_x = cx_f + raw_x * np.cos(ang) - raw_y * np.sin(ang)
        blob_y = cy_f + raw_x * np.sin(ang) + raw_y * np.cos(ang)

        # Step 2 — warp (blob_x/blob_y now exist)
        turb_strength = rng.uniform(0.015, 0.06)
        blob_x, blob_y = turbulent_warp(blob_x, blob_y, turb_strength, rng, seed_offset=seed * 0.0001)

        # Step 3 — nudge
        blob_x += rng.normal(0, 0.015)
        blob_y += rng.normal(0, 0.015)

        # Step 4 — distance from cluster center (uses blob_x/blob_y consistently)
        dist = np.sqrt((blob_x - cx_f)**2 + (blob_y - cy_f)**2)

        heat            = float(np.exp(-dist * 2.5))
        gradient_factor = float(np.exp(-dist * 1.2))
        color           = heat_to_rgb(heat, palette)

        blob_size  = int(rng.uniform(40, 120) * (0.5 + 0.5 * gradient_factor))
        blob_alpha = int(rng.uniform(3, 12) * gradient_factor + 2)
        blur_r     = int(rng.uniform(40, 100) * (0.5 + 0.5 * gradient_factor))

        blob, pad = draw_soft_blob(blob_size, color, blob_alpha, blur_r)
        image = _stamp(image, blob, px(blob_x) - blob_size // 2, py(blob_y) - blob_size // 2)

# ------- Filaments -------
NUM_FILAMENTS = int(rng.integers(5, 10) * density)
print(f"Drawing {NUM_FILAMENTS} filaments...")

for _ in range(NUM_FILAMENTS):
    cluster_idx = rng.integers(0, NUM_CLUSTERS)
    start_x_f   = cluster_x[cluster_idx]
    start_y_f   = cluster_y[cluster_idx]

    angle  = rng.uniform(0, 2 * np.pi)
    curve  = rng.uniform(-0.4, 0.4)
    length = rng.uniform(0.06, 0.20)

    NUM_POINTS = 50
    for j in range(NUM_POINTS):
        t = j / NUM_POINTS

        fx_f = start_x_f + t * length * np.cos(angle) \
               + curve * np.sin(t * np.pi) * np.cos(angle + np.pi / 2)
        fy_f = start_y_f + t * length * np.sin(angle) \
               + curve * np.sin(t * np.pi) * np.sin(angle + np.pi / 2)

        dist  = np.sqrt((fx_f - start_x_f)**2 + (fy_f - start_y_f)**2)
        heat  = float(np.exp(-dist * 8.0))
        color = heat_to_rgb(heat, palette)

        f_size  = int(rng.uniform(15, 50) * (1 - t * 0.8))
        f_alpha = int(rng.uniform(20, 60) * (1 - t) + 5)
        f_blur  = int(rng.uniform(8, 20)  * (1 - t * 0.5))

        blob, pad = draw_soft_blob(f_size, color, f_alpha, f_blur)
        image = _stamp(image, blob, px(fx_f) - f_size // 2, py(fy_f) - f_size // 2)

# ------- Dark Dust Lanes -------
NUM_LANES = rng.integers(3, 7)

for _ in range(NUM_LANES):
    # lanes originate from cluster edges, not centers
    cluster_idx = rng.integers(0, NUM_CLUSTERS)
    cx_f = cluster_x[cluster_idx]
    cy_f = cluster_y[cluster_idx]

    # offset from center so lane cuts through the cloud, not the core
    lane_offset_x = rng.normal(0, cluster_spread_x[cluster_idx] * 0.6)
    lane_offset_y = rng.normal(0, cluster_spread_y[cluster_idx] * 0.6)
    lane_x = cx_f + lane_offset_x
    lane_y = cy_f + lane_offset_y

    # each lane is a chain of dark blobs along a direction
    lane_angle  = rng.uniform(0, 2 * np.pi)
    lane_length = rng.uniform(0.08, 0.25)
    lane_curve  = rng.uniform(-0.3, 0.3)
    NUM_LANE_POINTS = 30

    for j in range(NUM_LANE_POINTS):
        t = j / NUM_LANE_POINTS

        # curved path same as filaments
        lx = lane_x + t * lane_length * np.cos(lane_angle) \
             + lane_curve * np.sin(t * np.pi) * np.cos(lane_angle + np.pi / 2)
        ly = lane_y + t * lane_length * np.sin(lane_angle) \
             + lane_curve * np.sin(t * np.pi) * np.sin(lane_angle + np.pi / 2)

        # apply turbulence to lane edges too so they feel organic
        lx, ly = turbulent_warp(lx, ly, 0.03, rng, seed_offset=seed * 0.0002)

        # dark brown/black — not pure black so it blends with the gas color
        dark_color = (8, 4, 2)   # very dark warm brown, tweak to taste
        lane_size  = int(rng.uniform(40, 120) * (1 - t * 0.5))  # wider at base
        lane_alpha = int(rng.uniform(180, 240) * (1 - t * 0.3)) # strong opacity
        lane_blur  = int(rng.uniform(15, 35))

        blob, pad = draw_soft_blob(lane_size, dark_color, lane_alpha, lane_blur)
        image = _stamp(image, blob, px(lx) - lane_size // 2, py(ly) - lane_size // 2)

# ------- Cloud Rims -------
for i in range(NUM_CLUSTERS):
    cx_f = cluster_x[i]
    cy_f = cluster_y[i]
    sx   = cluster_spread_x[i]
    sy   = cluster_spread_y[i]
    ang  = cluster_angle[i]

    NUM_RIM_POINTS = 60
    for j in range(NUM_RIM_POINTS):
        # place points around the ellipse boundary of each cluster
        theta = (j / NUM_RIM_POINTS) * 2 * np.pi

        raw_x = sx * np.cos(theta)
        raw_y = sy * np.sin(theta)

        rim_x = cx_f + raw_x * np.cos(ang) - raw_y * np.sin(ang)
        rim_y = cy_f + raw_x * np.sin(ang) + raw_y * np.cos(ang)

        # turbulence makes the rim jagged rather than a smooth oval
        rim_x, rim_y = turbulent_warp(rim_x, rim_y, 0.04, rng, seed_offset=seed * 0.0003)

        heat  = 0.3   # rims are mid-cool temperature
        color = heat_to_rgb(heat, palette)

        rim_size  = int(rng.uniform(20, 60))
        rim_alpha = int(rng.uniform(8, 20))
        rim_blur  = int(rng.uniform(20, 50))

        blob, pad = draw_soft_blob(rim_size, color, rim_alpha, rim_blur)
        image = _stamp(image, blob, px(rim_x) - rim_size // 2, py(rim_y) - rim_size // 2)
        


# ------- Highlight Stars -------
NUM_HIGHLIGHTS = 20
for _ in range(NUM_HIGHLIGHTS):
    cluster_idx = rng.integers(0, NUM_CLUSTERS)
    hx = px(cluster_x[cluster_idx] + rng.normal(0, 0.08))
    hy = py(cluster_y[cluster_idx] + rng.normal(0, 0.08))

    # bright core dot
    star_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw       = ImageDraw.Draw(star_layer)
    r          = rng.uniform(1, 3)
    draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 255, 255, 255))

    # soft glow around the highlight star
    glow, pad = draw_soft_blob(20, (255, 255, 255), 40, 10)
    image = _stamp(image, glow, hx - 10, hy - 10)
    image = add_layers(image, star_layer)

# ------- Save & Show -------
final = image.convert("RGB")
filename = f"nebula_{user_input.replace(' ', '_')}.png"
final.save(filename)
print(f"\nNebula saved as '{filename}'")
final.show()
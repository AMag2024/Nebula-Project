import matplotlib.pyplot as plt
import numpy as np
import hashlib

# ------- Helper Function -------
def heat_to_color(heat, palette):
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

    hot = hex_to_rgb(palette["hot"])
    mid = hex_to_rgb(palette["mid"])
    cold = hex_to_rgb(palette["cold"])

    if heat > 0.5:
        t = (heat - 0.5) * 2
        r = mid[0] + t * (hot[0] - mid[0])
        g = mid[1] + t * (hot[1] - mid[1])
        b = mid[2] + t * (hot[2] - mid[2])
    else:
        t = heat * 2
        r = cold[0] + t * (mid[0] - cold[0])
        g = cold[1] + t * (mid[1] - cold[1])
        b = cold[2] + t * (mid[2] - cold[2])

    return (r, g, b)

# ------- User Input -------
user_input = input("Enter a seed phrase or number: ")
print("\nCustomize your nebula (press Enter to use defaults):")
density_input = input("Density — low / medium / high (default: medium): ").strip().lower()
spread_input = input("Spread — tight / normal / wide (default: normal): ").strip().lower()
color_input = input("Color theme — pink / fire / blue / green / auto (default: auto): ").strip().lower()

# ------- Seed Generation -------
hash_bytes = hashlib.md5(user_input.encode()).hexdigest()
seed = int(hash_bytes, 16) % (2**32)
print(f"Your phrase '{user_input}' generated seed: {seed}")
rng = np.random.default_rng(seed)

# ------- Settings -------
density_map = {"low": 0.8, "medium": 1.5, "high": 3.0}
spread_map = {"tight": 0.1, "normal": 0.23, "wide": 0.3}
color_map = {"pink": 0, "fire": 1, "blue": 2, "green": 3}

density = density_map.get(density_input, 1.0)
spread = spread_map.get(spread_input, 0.12)

# ------- Palette -------
palette_options = [
    {"hot": "#ffffff", "mid": "#a855f7", "cold": "#1e0a3c"},  # purple
    {"hot": "#ffffff", "mid": "#ef4444", "cold": "#1a0500"},  # fire
    {"hot": "#ffffff", "mid": "#22d3ee", "cold": "#020d1a"},  # blue
    {"hot": "#ffffff", "mid": "#4ade80", "cold": "#011a08"},  # green
]
if color_input in color_map:
    palette = palette_options[color_map[color_input]]
else:
    palette = palette_options[seed % len(palette_options)]

# ------- Plot Setup -------
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.subplots_adjust(0, 0, 1, 1)
ax.axis('off')
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# ------- Star Generation -------
NUM_STARS = int(800 * density)
x = rng.uniform(0, 1, size=NUM_STARS)
y = rng.uniform(0, 1, size=NUM_STARS)
sizes = rng.uniform(0.75, 8, size=NUM_STARS)
ax.scatter(x, y, s=sizes, c='white', alpha=0.6, linewidths=0)

# ------- Cluster Setup -------
NUM_CLUSTERS = int(rng.integers(3, 7))
cluster_x = rng.uniform(0.2, 0.8, size=NUM_CLUSTERS)
cluster_y = rng.uniform(0.2, 0.8, size=NUM_CLUSTERS)
cluster_spread_x = rng.uniform(0.1, 0.35, size=NUM_CLUSTERS)   
cluster_spread_y = rng.uniform(0.1, 0.35, size=NUM_CLUSTERS)   
cluster_angle = rng.uniform(0, np.pi, size=NUM_CLUSTERS)

# ------- Glowing Cores -------
for i in range(NUM_CLUSTERS):
    cx, cy = cluster_x[i], cluster_y[i]
    for size, alpha in [(15000, 0.05), (10000, 0.07), (2000, 0.09), (400, 0.12)]:
        ax.scatter(cx, cy, s=size, c="white", alpha=alpha, linewidths=0)

# ------- Blob Generation -------
NUM_BLOBS = int(300 * density)
blobs_per_cluster = NUM_BLOBS // NUM_CLUSTERS

for i in range(NUM_CLUSTERS):
    cx, cy = cluster_x[i], cluster_y[i]
    sx = cluster_spread_x[i]
    sy = cluster_spread_y[i]
    angle = cluster_angle[i]

    for _ in range(blobs_per_cluster):
        dist_scale = rng.power(0.7) + 1.2

        raw_x = rng.normal(0, sx * dist_scale)
        raw_y = rng.normal(0, sy * dist_scale)

        blob_x = cx + raw_x * np.cos(angle) - raw_y * np.sin(angle)
        blob_y = cy + raw_x * np.sin(angle) + raw_y * np.cos(angle)

        blob_x += rng.normal(0, 0.015)
        blob_y += rng.normal(0, 0.015)

        dist = np.sqrt((blob_x - cx)**2 + (blob_y - cy)**2)

        heat = np.exp(-dist * 3.0)
        color = heat_to_color(heat, palette)

        gradient_factor = np.exp(-dist * 2.0)                 
        blob_alpha = rng.uniform(0.03, 0.10) * gradient_factor + 0.005
        blob_size = rng.uniform(8000, 25000) * (0.5 + 0.5 * gradient_factor)

        ax.scatter(blob_x, blob_y, s=blob_size, c=[color], alpha=blob_alpha, linewidths=0)

# ------- Filaments -------
NUM_FILAMENTS = int(rng.integers(6, 12) * density)

for _ in range(NUM_FILAMENTS):
    cluster_idx = rng.integers(0, NUM_CLUSTERS)
    start_x = cluster_x[cluster_idx]
    start_y = cluster_y[cluster_idx]

    angle = rng.uniform(0, 2 * np.pi)
    curve = rng.uniform(-0.4, 0.4)
    length = rng.uniform(0.05, 0.18)
    
    NUM_POINTS = 40
    for j in range(NUM_POINTS):
        t = j / NUM_POINTS

        fx = start_x + t * length * np.cos(angle) + curve * np.sin(t * np.pi) * np.cos(angle + np.pi / 2)
        fy = start_y + t * length * np.sin(angle) + curve * np.sin(t * np.pi) * np.sin(angle + np.pi / 2)

        # distance from cluster center for heat coloring
        dist = np.sqrt((fx - start_x)**2 + (fy - start_y)**2)
        heat = np.exp(-dist * 8.0)
        color = heat_to_color(heat, palette)

        alpha = rng.uniform(0.06, 0.18) * (1 - t) + 0.01
        size = rng.uniform(200, 1200) * (1 - t * 0.8)

        ax.scatter(fx, fy, s=size, c=[color], alpha=alpha, linewidths=0)

# ------- Highlight Stars -------
NUM_HIGHLIGHTS = 15
for _ in range(NUM_HIGHLIGHTS):
    cluster_idx = rng.integers(0, NUM_CLUSTERS)
    hx = cluster_x[cluster_idx] + rng.normal(0, 0.08)
    hy = cluster_y[cluster_idx] + rng.normal(0, 0.08)
    ax.scatter(hx, hy, s=rng.uniform(5, 25), c="white", alpha=1.0, linewidths=0)

plt.show()
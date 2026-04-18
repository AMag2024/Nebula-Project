import matplotlib.pyplot as plt
import numpy as np
import hashlib

NUM_STARS = 2000


user_input = input("Enter a seed phrase or number: ")
print("\nCustomize your nebula (press Enter to use defaults):")

density_input = input("Density — low / medium / high (default: medium): ").strip().lower()
spread_input = input("Spread — tight / normal / wide (default: normal): ").strip().lower()
color_input = input("Color theme — pink / fire / blue / green / auto (default: auto): ").strip().lower()

#------- Seed Generation -------
hash_bytes = hashlib.md5(user_input.encode()).hexdigest()
seed = int(hash_bytes, 16) % (2**32)
print(f"Your phrase '{user_input}' generated seed: {seed}")
rng = np.random.default_rng(seed)

#---- Plot Setup ----
fig, ax = plt.subplots()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.subplots_adjust(0,0,1,1)  # Remove margins
ax.axis('off')  # Hide axes
ax.set_xticks([])
ax.set_yticks([])

for spine in ax.spines.values():
    spine.set_visible(False)

fig.patch.set_facecolor('black')
ax.set_facecolor('black')

#------- Star Generation -------
x = rng.uniform(0, 1, size=NUM_STARS)
y = rng.uniform(0, 1, size=NUM_STARS)

sizes = rng.uniform(0.75, 8, size=NUM_STARS)
brightness = rng.uniform(0.02,0.80, size=NUM_STARS)

ax.scatter(x, y, s=sizes, c='white', alpha=brightness)


#------- Nebula Generation -------

palette_options = [
    ["#ff6ec7", "#a855f7", "#6366f1"],  # pink/purple
    ["#f97316", "#ef4444", "#fbbf24"],  # red/orange
    ["#22d3ee", "#3b82f6", "#6366f1"],  # blue/cyan
    ["#4ade80", "#22d3ee", "#a855f7"],  # green/teal
]

palette = palette_options[seed % len(palette_options)]

NUM_BLOBS = 300
NUM_CLUSTERS = rng.integers(3, 7)
cluster_x = rng.uniform(0.2, 0.8, size=NUM_CLUSTERS)
cluster_y = rng.uniform(0.2, 0.8, size=NUM_CLUSTERS)

# give each cluster its own personality
cluster_spread_x = rng.uniform(0.05, 0.2, size=NUM_CLUSTERS)  # width
cluster_spread_y = rng.uniform(0.05, 0.2, size=NUM_CLUSTERS)  # height (different = ellipse)
cluster_angle = rng.uniform(0, np.pi, size=NUM_CLUSTERS)       # rotation angle

density_map = {"low": 0.8, "medium": 1.5, "high": 3.0}
spread_map = {"tight": 0.1, "normal": 0.23, "wide": 0.3}
color_map = {"pink": 0, "fire": 1, "blue": 2, "green": 3}

density = density_map.get(density_input, 1.0)
spread = spread_map.get(spread_input, 0.12)

if color_input in color_map:
    palette = palette_options[color_map[color_input]]
else:
    palette = palette_options[seed % len(palette_options)]  # auto from seed



for _ in range(NUM_BLOBS):
    cluster_idx = rng.integers(0, NUM_CLUSTERS)
    cx, cy = cluster_x[cluster_idx], cluster_y[cluster_idx]
    color = palette[rng.integers(0, len(palette))]
    sx = cluster_spread_x[cluster_idx]
    sy = cluster_spread_y[cluster_idx]
    angle = cluster_angle[cluster_idx]

    raw_x = rng.normal(0, sx)
    raw_y = rng.normal(0, sy)
    

    blob_x = cx + raw_x * np.cos(angle) - raw_y * np.sin(angle)
    blob_y = cy + raw_x * np.sin(angle) + raw_y * np.cos(angle)
    blob_size = rng.uniform(3000, 15000)
    blob_alpha = rng.uniform(0.04, 0.15)

    # add a small random nudge for extra irregularity
    blob_x += rng.normal(0, 0.02)
    blob_y += rng.normal(0, 0.02)

    NUM_STARS = int(800 * density)
    NUM_BLOBS = int(300 * density)
    # use spread instead of the hardcoded 0.12 in the blob scatter
    blob_x = cx + rng.normal(0, spread)
    blob_y = cy + rng.normal(0, spread)
    
    # Find the average center of your clusters
    core_x = np.mean(cluster_x)
    core_y = np.mean(cluster_y)

    for i in range(NUM_CLUSTERS):
        cx, cy = cluster_x[i], cluster_y[i]
    
    for size, alpha in [(10000, 0.02), (5000, 0.03), (1000, 0.06), (200, 0.1)]:
        ax.scatter(cx, cy, s=size, c="white", alpha=alpha, linewidths=0)

    NUM_HIGHLIGHTS = 15
    for _ in range(NUM_HIGHLIGHTS):
        cluster_idx = rng.integers(0, NUM_CLUSTERS)
        hx = cluster_x[cluster_idx] + rng.normal(0, 0.08)
        hy = cluster_y[cluster_idx] + rng.normal(0, 0.08)
        ax.scatter(hx, hy, s=rng.uniform(5, 25), c="white", alpha=1.0, linewidths=0)

    ax.scatter(blob_x, blob_y, s=blob_size, c=color, alpha=blob_alpha, linewidths=0)


NUM_HIGHLIGHTS = 15
for _ in range(NUM_HIGHLIGHTS):
    cluster_idx = rng.integers(0, NUM_CLUSTERS)
    hx = cluster_x[cluster_idx] + rng.normal(0, 0.08)
    hy = cluster_y[cluster_idx] + rng.normal(0, 0.08)
    ax.scatter(hx, hy, s=rng.uniform(5, 25), c="white", alpha=1.0, linewidths=0)



plt.show()



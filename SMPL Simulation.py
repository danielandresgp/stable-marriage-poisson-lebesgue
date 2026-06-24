#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python3
"""
Stable Marriage of Poisson and Lebesgue (with Random Appetites)
Jupyter-friendly script with user input for all parameters + dynamic titles.

References:
- Hoffman, Holroyd, Peres (Ann. Probab. 2006)
- Hoffman, Holroyd, Peres (arXiv:0909.5325, 2009) - random appetites
"""

import numpy as np
import matplotlib.pyplot as plt
import heapq
import os
from matplotlib.colors import ListedColormap

try:
    from tqdm.notebook import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


# ============================================================
#                    USER INPUT SECTION
# ============================================================

print("=" * 70)
print("STABLE MARRIAGE OF POISSON AND LEBESGUE - PARAMETER INPUT")
print("=" * 70)

# ---------------- Model Parameters ----------------
print("\n--- MODEL PARAMETERS ---")

print("""
M (Number of centers):
    Controls how many Poisson points (centers) are placed in the box.
    Higher M → more centers, smaller average territories.
    Suggested values: 50–200 for visualization, 500+ for statistics.
""")
M = int(input("Enter M (default=100): ") or 100)

print("""
L (Box side length):
    The simulation runs on a square box of side L (area = L²).
    With intensity 1, expected number of centers ≈ L².
    Usually set so that L = sqrt(M) for intensity ≈ 1.
    Suggested: L = sqrt(M) or L=10 for M=100.
""")
L = float(input("Enter L (default=10.0): ") or 10.0)

print("""
N (Grid resolution):
    Discretizes the continuous space into an N × N grid of pixels.
    Higher N → more accurate approximation of the continuous model,
    but slower computation and more memory.
    Suggested: 200–400 for good balance, 500+ for high precision.
""")
N = int(input("Enter N (default=300): ") or 300)

print("""
APPETITE_TYPE:
    - "constant"     → All centers have the same fixed appetite α.
    - "exponential"  → Appetites drawn from Exponential distribution (most natural).
    - "uniform"      → Appetites drawn from Uniform distribution.
    - "voronoi"      → Infinite appetite → recovers classical Voronoi tessellation.
""")
APPETITE_TYPE = input('Enter APPETITE_TYPE ["constant"/"exponential"/"uniform"/"voronoi"] (default="exponential"): ').strip().lower() or "exponential"

print("""
APPETITE_MEAN:
    Mean appetite per center (only used for "constant", "exponential", "uniform").
    For "constant": this is the fixed value α.
    For random appetites: this is the expected value E[α].
    Suggested: 1.0 (critical regime), or very large (e.g. 500) to approximate Voronoi.
""")
APPETITE_MEAN = float(input("Enter APPETITE_MEAN (default=1.0): ") or 1.0)


# ---------------- Figure Rendering Parameters ----------------
print("\n--- FIGURE RENDERING PARAMETERS ---")

print("""
DPI (Dots Per Inch):
    Resolution of the saved PNG image.
    Higher DPI → sharper figure when printing or zooming in.
    Does NOT affect the simulation itself.
    Suggested: 150 (screen), 300 (publication quality), 600 (very high res).
""")
DPI = int(input("Enter DPI (default=300): ") or 300)

print("""
STRIPE_WIDTH:
    Width of each concentric stripe inside territories (in the same units as L).
    Smaller value → more/finer stripes (better visual detail of growth process).
    Larger value → fewer, thicker stripes.
    Suggested: 0.10–0.15 for nice detail, 0.20–0.25 for cleaner look.
""")
STRIPE_WIDTH = float(input("Enter STRIPE_WIDTH (default=0.12): ") or 0.12)

print("""
USE_STRIPED_TERRITORIES:
    True  → Paper-style visualization with concentric stripes + per-territory colors.
    False → Simple one random color per territory (faster, less informative).
""")
USE_STRIPED_TERRITORIES_input = input("Use striped territories? [y/n] (default=y): ").strip().lower()
USE_STRIPED_TERRITORIES = USE_STRIPED_TERRITORIES_input != "n"


# ============================================================
#                 GENERATE APPETITES + DYNAMIC TITLE
# ============================================================

if APPETITE_TYPE == "constant":
    appetites = np.full(M, APPETITE_MEAN)
    model_title = f"Stable Marriage of Poisson and Lebesgue with Constant Appetites (α = {APPETITE_MEAN})"
elif APPETITE_TYPE == "exponential":
    appetites = np.random.exponential(scale=APPETITE_MEAN, size=M)
    model_title = f"Stable Marriage of Poisson and Lebesgue with Exponentially Distributed Appetites (E[α] = {APPETITE_MEAN})"
elif APPETITE_TYPE == "uniform":
    appetites = np.random.uniform(low=0.5*APPETITE_MEAN, high=1.5*APPETITE_MEAN, size=M)
    model_title = f"Stable Marriage of Poisson and Lebesgue with Uniformly Distributed Appetites (E[α] = {APPETITE_MEAN})"
elif APPETITE_TYPE == "voronoi":
    appetites = np.full(M, np.inf)
    model_title = "Voronoi Tessellation of Poisson Points"
else:
    raise ValueError("Invalid APPETITE_TYPE. Choose: constant / exponential / uniform / voronoi")


print("\n" + "=" * 70)
print("PARAMETERS SUMMARY")
print("=" * 70)
print(f"M = {M}, L = {L}, N = {N}")
print(f"APPETITE_TYPE = {APPETITE_TYPE}, APPETITE_MEAN = {APPETITE_MEAN}")
print(f"DPI = {DPI}, STRIPE_WIDTH = {STRIPE_WIDTH}, STRIPED = {USE_STRIPED_TERRITORIES}")
print("=" * 70)


# ============================================================
#                    SIMULATION
# ============================================================

centers = np.random.uniform(0, L, size=(M, 2))

x = np.linspace(0, L, N, endpoint=False) + L / (2 * N)
y = np.linspace(0, L, N, endpoint=False) + L / (2 * N)
grid_x, grid_y = np.meshgrid(x, y, indexing='xy')
grid = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)
G = grid.shape[0]
pixel_area = (L / N) ** 2

# Precompute distances
print("\nPrecomputing distances...")
sorted_pix = [None] * M
sorted_dist = [None] * M
for c in range(M):
    cx, cy = centers[c]
    dx = np.abs(grid[:, 0] - cx)
    dx = np.minimum(dx, L - dx)
    dy = np.abs(grid[:, 1] - cy)
    dy = np.minimum(dy, L - dy)
    dists = np.hypot(dx, dy)
    order = np.argsort(dists)
    sorted_pix[c] = order
    sorted_dist[c] = dists[order]

# Allocation
print("Running stable allocation...")
claimed = np.full(G, -1, dtype=np.int32)
remaining = appetites.copy().astype(float)

heap = []
for c in range(M):
    if len(sorted_pix[c]) > 0:
        heapq.heappush(heap, (sorted_dist[c][0], c, 0))

while heap:
    _, c, idx = heapq.heappop(heap)
    pix = sorted_pix[c][idx]
    if claimed[pix] != -1:
        if idx + 1 < len(sorted_pix[c]):
            heapq.heappush(heap, (sorted_dist[c][idx + 1], c, idx + 1))
        continue
    if remaining[c] > 0:
        claimed[pix] = c
        remaining[c] = max(0.0, remaining[c] - pixel_area)
        if remaining[c] > 0 and idx + 1 < len(sorted_pix[c]):
            heapq.heappush(heap, (sorted_dist[c][idx + 1], c, idx + 1))

# Post-process unclaimed pixels
unclaimed = np.where(claimed == -1)[0]
if len(unclaimed) > 0:
    for pix in unclaimed:
        cx, cy = grid[pix]
        best_c, best_d = -1, np.inf
        for c in range(M):
            if remaining[c] > 0:
                dx = min(abs(centers[c, 0] - cx), L - abs(centers[c, 0] - cx))
                dy = min(abs(centers[c, 1] - cy), L - abs(centers[c, 1] - cy))
                d = np.hypot(dx, dy)
                if d < best_d:
                    best_d, best_c = d, c
        if best_c >= 0:
            claimed[pix] = best_c
            remaining[best_c] = max(0., remaining[best_c] - pixel_area)

territories = np.bincount(claimed[claimed >= 0], minlength=M) * pixel_area


# ============================================================
#                    VISUALIZATION
# ============================================================

fig, ax = plt.subplots(figsize=(11, 10))

if USE_STRIPED_TERRITORIES:
    # Use golden ratio for better hue separation (reduces similar colors in neighboring territories)
    golden_ratio = (1 + np.sqrt(5)) / 2
    hues = np.mod(np.arange(M) * golden_ratio, 1.0)
    base_colors = np.zeros((M, 3))
    for c in range(M):
        # Higher contrast between dark and light versions
        base_colors[c] = np.array(plt.cm.hsv(hues[c])[:3]) * 0.8 + 0.05

    dist_to_owner = np.full(G, np.inf)
    for c in range(M):
        mask = (claimed == c)
        if np.any(mask):
            cx, cy = centers[c]
            dx = np.abs(grid[mask, 0] - cx)
            dx = np.minimum(dx, L - dx)
            dy = np.abs(grid[mask, 1] - cy)
            dy = np.minimum(dy, L - dy)
            dist_to_owner[mask] = np.hypot(dx, dy)

    # Safe computation of stripe_index (handles np.inf from unclaimed pixels)
    stripe_index = np.zeros(G, dtype=int)
    valid = np.isfinite(dist_to_owner)
    stripe_index[valid] = (np.floor(dist_to_owner[valid] / STRIPE_WIDTH) % 2).astype(int)

    vis_rgb = np.zeros((G, 3))
    for c in range(M):
        mask = (claimed == c)
        if np.any(mask):
            dark = np.clip(base_colors[c] * 0.80, 0, 1)
            light = np.clip(base_colors[c] * 1.45 + 0.10, 0, 1)
            vis_rgb[mask & (stripe_index == 0)] = dark
            vis_rgb[mask & (stripe_index == 1)] = light

    unclaimed_mask = (claimed == -1)
    if np.any(unclaimed_mask):
        vis_rgb[unclaimed_mask] = [0.92, 0.92, 0.92]
    vis_rgb = vis_rgb.reshape((N, N, 3))
    im = ax.imshow(vis_rgb, origin='lower', extent=[0, L, 0, L],
                   interpolation='nearest', aspect='equal')
else:
    owner_grid = claimed.reshape((N, N))
    owner_grid = np.where(owner_grid == -1, M, owner_grid)
    np.random.seed(123)
    colors = np.random.rand(M, 3)
    colors = np.vstack([colors, [[0.93, 0.93, 0.93]]])
    cmap = ListedColormap(colors)
    im = ax.imshow(owner_grid, cmap=cmap, origin='lower',
                   extent=[0, L, 0, L], interpolation='nearest', aspect='equal')

ax.scatter(centers[:, 0], centers[:, 1],
           c='black', s=14, marker='o',
           edgecolors='white', linewidths=0.6, zorder=5,
           label=f'Poisson centers (M={M})')

ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title(model_title, fontsize=13, pad=12)
ax.legend(loc='upper right', fontsize=9)

plt.tight_layout()

os.makedirs("artifacts", exist_ok=True)
fig.savefig("artifacts/stable_marriage_custom.png", dpi=DPI, bbox_inches='tight', facecolor='white')
print(f"\n✓ Figure saved to: artifacts/stable_marriage_custom.png (DPI={DPI})")
plt.show()

print("\nSimulation complete.")


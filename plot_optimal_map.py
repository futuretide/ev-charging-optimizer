# File: plot_optimal_map.py

import os
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

def main():
    # 1. Project root is the directory this script lives in
    ROOT = os.path.abspath(os.path.dirname(__file__))

    # 2. Data paths
    TRACTS_FILE = os.path.join(ROOT, "data", "cleaned", "merged_data.geojson")
    CAND_FILE   = os.path.join(ROOT, "data", "processed", "candidate_sites_prepped.geojson")
    OPT_FILE    = os.path.join(ROOT, "data", "processed", "optimal_sites_dgal.geojson")
    OUT_PNG     = os.path.join(ROOT, "figures", "optimal_sites_map.png")

    # 3. Load layers
    tracts     = gpd.read_file(TRACTS_FILE)
    candidates = gpd.read_file(CAND_FILE)
    selected   = gpd.read_file(OPT_FILE)

    # 4. Reproject to Web Mercator for basemap overlay
    tracts_3857     = tracts.to_crs(epsg=3857)
    candidates_3857 = candidates.to_crs(epsg=3857)
    selected_3857   = selected.to_crs(epsg=3857)

    # 5. Plot setup
    fig, ax = plt.subplots(figsize=(10, 10))
    tracts_3857.boundary.plot(
        ax=ax, edgecolor="#666666", linewidth=0.5, zorder=2
    )

    # 6. Add a basemap
    try:
        ctx.add_basemap(
            ax,
            source=ctx.providers.Stamen.TerrainBackground,
            zoom=12
        )
    except Exception:
        ctx.add_basemap(
            ax,
            source=ctx.providers.OpenStreetMap.Mapnik,
            zoom=12
        )

    # 7. Plot all candidates
    candidates_3857.plot(
        ax=ax,
        markersize=10,
        alpha=0.6,
        color="#1f77b4",
        label="All candidates",
        zorder=3
    )

    # 8. Plot selected sites
    selected_3857.plot(
        ax=ax,
        markersize=120,
        marker="*",
        color="#d62728",
        edgecolor="k",
        linewidth=0.5,
        label="Selected sites",
        zorder=4
    )

    # 9. Legend & title
    ax.legend(frameon=True, loc="upper right")
    ax.set_title("Optimal EV Charger Sites (DGAL Model)", fontsize=16)
    ax.axis("off")

    # 10. Save & show
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    print(f"✅ Map saved to {OUT_PNG}")
    plt.show()


if __name__ == "__main__":
    main()

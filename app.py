# File: app.py

import os
import sys
from pathlib import Path

# Allow importing scripts/ as a module
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DEFAULT_N_SITES, DEFAULT_COVERAGE_WEIGHT, DEFAULT_MIN_DISTANCE

import streamlit as st
import geopandas as gpd
import folium
from folium import (
    FeatureGroup, LayerControl, Map, TileLayer,
    CircleMarker, Marker, Icon, Element
)
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from scripts.dgal_model import optimize_dgal

st.set_page_config(page_title="EV Charger Siting (DGAL)", layout="wide")
st.title("⚡ EV Charger Siting (DGAL Model)")

# ------------------------
# Session state init
# ------------------------
for key in ("run_flag", "selected_gdf", "obj_val"):
    if key not in st.session_state:
        st.session_state[key] = None

def reset():
    st.session_state.run_flag      = False
    st.session_state.selected_gdf  = None
    st.session_state.obj_val       = None

# ------------------------
# Sidebar
# ------------------------
st.sidebar.header("Model parameters")
N_sites    = st.sidebar.slider("Number of chargers",   10, 200, DEFAULT_N_SITES)
coverage_w = st.sidebar.slider("Coverage weight",      0.0, 100.0, DEFAULT_COVERAGE_WEIGHT)
min_dist   = st.sidebar.slider("Min-distance (m)",     0.0, 2000.0, DEFAULT_MIN_DISTANCE)

st.sidebar.markdown("---")
if st.sidebar.button("Run Optimization"):
    with st.spinner("Solving DGAL model…"):
        sel, obj = optimize_dgal(
            candidate_geojson=os.path.join("data","processed","candidate_sites_prepped.geojson"),
            tract_geojson   =os.path.join("data","cleaned","merged_data.geojson"),
            N_sites         =N_sites,
            output_path     =None,
            demand_field    ="demand_score",
            coverage_weight =coverage_w,
            min_distance    =min_dist
        )
    st.session_state.selected_gdf = sel
    st.session_state.obj_val      = obj
    st.session_state.run_flag     = True

if st.sidebar.button("Reset"):
    reset()

st.sidebar.markdown("---")
st.sidebar.header("Layer visibility")
show_candidates = st.sidebar.checkbox("Show candidate sites", value=True)
show_optimal    = st.sidebar.checkbox("Show optimal sites",   value=True)

# ------------------------
# Reverse geocoder (cached)
# ------------------------
@st.cache_data(show_spinner=False)
def get_street(lat: float, lon: float) -> str:
    geolocator = Nominatim(user_agent="ev_siting_app")
    try:
        loc = geolocator.reverse((lat, lon), exactly_one=True, addressdetails=True)
    except Exception:
        return f"{lat:.5f}, {lon:.5f}"
    if not loc or "address" not in loc.raw:
        return f"{lat:.5f}, {lon:.5f}"
    addr = loc.raw["address"]
    for key in ("road", "pedestrian", "footway", "path", "house_number"):
        if key in addr:
            return addr[key]
    return f"{lat:.5f}, {lon:.5f}"

# ------------------------
# Main display
# ------------------------
if st.session_state.run_flag and st.session_state.selected_gdf is not None:
    st.success(f"✅ Done! Objective value: {st.session_state.obj_val:.2f}")

    # Load & reproject data
    candidates = (
        gpd.read_file(os.path.join("data","processed","candidate_sites_prepped.geojson"))
           .to_crs(epsg=4326)
    )
    optimal = st.session_state.selected_gdf.to_crs(epsg=4326)

    lat0 = float(candidates.geometry.y.mean())
    lon0 = float(candidates.geometry.x.mean())

    m = Map(location=[lat0, lon0], zoom_start=11, tiles=None, control_scale=True)

    # Basemaps
    TileLayer(
        tiles="https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
        attr="Map tiles by Stamen Design (CC BY 3.0), data © OpenStreetMap contributors",
        name="Stamen Terrain",
        overlay=False,
        control=True
    ).add_to(m)
    TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        name="OpenStreetMap",
        overlay=False,
        control=True
    ).add_to(m)

    # Feature groups
    fg_cand = FeatureGroup(name="Candidate sites", show=show_candidates)
    fg_opt  = FeatureGroup(name="Optimal sites",   show=show_optimal)

    # Candidate dots
    if show_candidates:
        for _, r in candidates.iterrows():
            CircleMarker(
                location=(r.geometry.y, r.geometry.x),
                radius=3, color="#1f77b4", fill=True,
                fill_opacity=0.5, weight=0
            ).add_to(fg_cand)

    # Optimal pins with street tooltips and coordinate popups
    if show_optimal:
        for _, r in optimal.iterrows():
            lat, lon = r.geometry.y, r.geometry.x
            street = get_street(lat, lon)
            Marker(
                location=(lat, lon),
                icon=Icon(icon="map-pin", prefix="fa", color="red"),
                tooltip=street,                              # hover shows street
                popup=f"📍 {lat:.5f}, {lon:.5f}"             # click shows coords
            ).add_to(fg_opt)

    fg_cand.add_to(m)
    fg_opt.add_to(m)
    LayerControl(collapsed=False).add_to(m)

    # Legend box
    legend_html = """
     <div style="
       position: fixed;
       bottom: 50px; left: 50px; width: 180px;
       background-color: rgba(255,255,255,0.9);
       border:2px solid grey; z-index:9999;
       font-size:14px; color:black; padding:10px;
     ">
       <b>Legend</b><br>
       <i style="background:#1f77b4; border-radius:50%; display:inline-block;
                 width:10px; height:10px; margin-right:5px;"></i>Candidate sites<br>
       <i class="fa fa-map-pin" style="color:red; margin-right:5px;"></i>Optimal sites
     </div>
    """
    m.get_root().html.add_child(Element(legend_html))

    st.header("📍 Selected Sites Map")
    st_folium(m, width="100%", height=700, returned_objects=[])

else:
    st.info("Adjust parameters and click **Run Optimization** to generate the map.")

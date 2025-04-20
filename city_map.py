# make_city_map_tooltip_reds.py

import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear

# ─── 1) Read & prep your data ───────────────────────────────────────────────
gdf = gpd.read_file("tl_2024_06_place.shp")
gdf = gdf[(gdf.LSAD == "25") & (gdf.STATEFP == "06")]
gdf["CITY_NAME"] = gdf.NAME.str.upper()

city_data = pd.read_csv("cleaned_citydatademoCSV.csv")
city_data["CITY_NAME"] = city_data["City Name"].str.upper()

vars_to_plot = [
    "Latino %", "White %", "Black %", "Asian %",
    "Native %", "PI %", "Other %", "Multiracial %",
    "Total Population", "Median Household Income"
]
initial = vars_to_plot[0]

merged = (
    gdf[["CITY_NAME", "geometry"]]
      .merge(city_data[["CITY_NAME"] + vars_to_plot], on="CITY_NAME")
)

# ─── 2) Precompute Branca Reds colormaps ────────────────────────────────────
colormaps = {
    var: linear.Reds_09.scale(merged[var].min(), merged[var].max())
    for var in vars_to_plot
}

# ─── 3) Build the map (no default tiles) ──────────────────────────────────
m = folium.Map(location=[34.0, -118.2], zoom_start=9, tiles=None)
# Add Carto basemap (not in LayerControl)
folium.TileLayer(
    tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
    attr="&copy; CARTO",
    control=False
).add_to(m)

# ─── 4) Add each var as a GeoJson base-layer with hover tooltip ────────────
def make_style_fn(var):
    cmap = colormaps[var]
    def style_fn(feat):
        val = feat["properties"][var]
        return {
            "fillColor":   cmap(val),
            "color":       "black",
            "weight":      0.3,
            "fillOpacity": 0.7
        }
    return style_fn

for var in vars_to_plot:
    folium.GeoJson(
        merged.__geo_interface__,
        style_function=make_style_fn(var),
        tooltip=folium.GeoJsonTooltip(
            fields=[var],
            aliases=[f"{var}:"],
            localize=True
        ),
        name=var,
        overlay=False,            # radio‐button style
        show=(var == initial)     # only initial on load
    ).add_to(m)

# ─── 5) Add radio‐button LayerControl & save ───────────────────────────────
folium.LayerControl(collapsed=False).add_to(m)
m.save("city_map_tooltip_reds.html")

print("✅ city_map_tooltip_reds.html created. Open it to verify Folium Reds palette with hover tooltips.")

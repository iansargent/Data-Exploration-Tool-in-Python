import pyogrio

flood_gdf = pyogrio.read_dataframe(
    "/Users/iansargent/Desktop/ORCA/Steamlit App Testing/VT_Flood_Hazard.geojson"
)

pyogrio.write_dataframe(flood_gdf, "VT_Flood_Hazard.fgb")

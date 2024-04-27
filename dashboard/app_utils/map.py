
import geopandas as gpd
import pandas as pd
from shiny.ui import tags
from ipyleaflet import Map


def layer_exists(
        m: Map,
          name: str):
    """
    Check if a layer exists in a map.

    Args:
        m: ipyleaflet.Map
        name: str
    
    Returns: bool - True if the layer exists, False otherwise
    
    """
    for layer in m.layers:
        if layer.name == name:
            return True
    return False


def get_layer(
        m: Map, 
        name: str
        ):
    """
    Get a layer from a map by name.

    Args:
        m: ipyleaflet.Map
        name: str

    Returns: ipyleaflet.Layer or None
    """
    for layer in m.layers:
        if layer.name == name:
            return layer
    return None


from ipyleaflet import Map, basemaps, basemap_to_tiles, GeoData, LayersControl
def generate_basemap(south_yorkshire: gpd.GeoDataFrame):
        ## Map ----------------------------------------------------------------------
    m = Map(width="100%", height="100%", zoom=13)
    print("Init Map")
    imagery = basemap_to_tiles(basemaps.Esri.WorldImagery)
    imagery.base = True
    imagery.name = "Imagery"

    m.add_layer(imagery)

    bbox = south_yorkshire.total_bounds

    m.fit_bounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]])

    m.add_control(LayersControl(position="bottomleft", collapsed=False))

    sy_geo = GeoData(
        geo_dataframe=south_yorkshire,
        name="South Yorkshire Boundary",
        style={
            "color": "pink",
            "fillColor": "pink",
            "opacity": 0.6,
            "weight": 1.9,
            "dashArray": "2",
            "fillOpacity": 0,
        },

    )
    m.add_layer(sy_geo)

    return m


def main():
    bat_records  = gpd.read_parquet("dashboard/data/bat-records.parquet")
    
    bat_records['popup'] = bat_records.apply(record_popup, axis=1)
    # geet one to check
    bat_records.iloc[0].popup
    pass

if __name__ == '__main__':
    main()

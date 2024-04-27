"Functions for loading and processing data for the dashboard"
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxr
import matplotlib.pyplot as plt
from matplotlib.colors import Colormap
from matplotlib.cm import get_cmap
from gcsfs import GCSFileSystem




def normalize(array:np.ndarray, vmin=None, vmax=None):
    """
    This function normalizes an array to be between 0 and 1.
    """
    if vmin is None or vmax is None:
        array = (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array))
    else:
        # clip the values to the min and max
        array = array.clip(vmin, vmax)
        array = (array - vmin) / (vmax - vmin)
    return array


def array_to_rgb(array:np.ndarray, colormap="viridis", vmin=None, vmax=None):
    """
    This function converts an array to a RGB array using a colormap.
    """
    colormap_fn = get_cmap(colormap)
    # Normalize the band
    array = normalize(array, vmin, vmax)
    # apply the colormap to convert to RGD
    rgb = colormap_fn(array)
    return rgb



def write_tif_to_pngs(
        dataset:xr.Dataset,
        out_dir:Path, 
        colormap="viridis", 
        vmin=None, 
        vmax=None, 
        overwrite=False
        ) -> tuple[dict[str, Path], tuple, int]:
    """
    This function converts each band of a tif file to a RGB array and writes it to a PNG file.
    """
    # Get the band names
    band_names = dataset.data_vars.keys()
    output_paths  = {}

    colormap_fn = get_cmap(colormap)
    tif_bounds = dataset.rio.bounds()
    tif_crs = dataset.rio.crs.to_epsg()
    # Loop through each band
    for band_name in band_names:
        out_path = out_dir/f"{band_name}.png"
        output_paths[band_name] = out_path

        if out_path.exists() and not overwrite:
            # Skip if the file already exists and user doesn't want to overwrite
            continue

        # Get the band
        band = dataset[band_name].values
        # flip the y axis to match the tif
        band = np.flipud(band)
        # Normalize the band
        band = normalize(band, vmin, vmax)
        # apply the colormap to convert to RGD
        rgb = colormap_fn(band)
        # Write the PNG file
        plt.imsave(out_path, rgb)
        

    return output_paths, tif_bounds, tif_crs


#file_paths = download_data()
def setup_paths():
    remote_dir = "gs://sygb-data/app_data"
    file_dependencies = {
        "results" : "results.csv",
        "bat_records" : "bat-records.parquet",
        "predictions" : "predictions_cog.tif",
        "boundary" : "boundary.parquet",
        "partial_dependence" : "partial-dependence-data.parquet",
    }
    file_paths = {}
    for key, file in file_dependencies.items():
        file_paths[key] = f"{remote_dir}/{file}"
    
    return file_paths



def load_results_df() -> pd.DataFrame:
    """
    This function loads the results dataframe
    """
    # Load the results data
    results_df = pd.read_csv("https://storage.googleapis.com/sygb-data/app_data/results.csv")
    # Return the dataframe
    return results_df


def load_training_data() -> gpd.GeoDataFrame:
    """
    This function loads the training data
    """
    # Load the training data
    uri = "gs://sygb-data/app_data/bat-records.parquet"
    with GCSFileSystem().open(uri) as file:
        training_data_gdf = gpd.read_parquet(file)
    training_data_gdf = training_data_gdf.to_crs(4326)
    # Return the dataframe
    return training_data_gdf



def load_predictions() -> xr.Dataset:
    """
    Load the model predictions array.

    This function loads the tif and processes it to be in the correct format for the dashboard.
    """
    url = "https://storage.googleapis.com/sygb-data/app_data/predictions_cog.tif"
    predictions = rxr.open_rasterio(url)
    predictions.coords["band"] = list(predictions.attrs["long_name"])
    # Set the nodata appropriately
    nodata = -1
    predictions = predictions.where(predictions >= 0, np.nan)

    # convert to a dataset to allow band name indexing
    predictions = predictions.to_dataset(dim="band")
    # Convert back to 0-1
    predictions = predictions / 100

    return predictions


def load_partial_dependence_data() -> pd.DataFrame:
    """
    This function loads the partial dependence data
    """
    path = "https://storage.googleapis.com/sygb-data/app_data/partial-dependence-data.parquet"
    return pd.read_parquet(path)



def calculate_dependence_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates the range of values for each feature.

    Args:
        df: pd.DataFrame - The dataframe of partial dependence values.

    Returns: pd.DataFrame - The dataframe of feature ranges.
    """
    # Group by the latin name, activity type and feature
    df = (
        df.groupby(["latin_name", "activity_type", "feature"])["average"]
        .apply(lambda x: x.max() - x.min())
        .reset_index()
    )
    # Return the dataframe
    return df


def load_south_yorkshire():
    """
    This function loads the counties data which is a large file and filters it for those in south yorkshire
    """
    # Load the counties data
    uri = "gs://sygb-data/app_data/boundary.parquet"
    with GCSFileSystem().open(uri) as file:
        boundary = gpd.read_parquet(file)
    # Return the dataframe
    return boundary
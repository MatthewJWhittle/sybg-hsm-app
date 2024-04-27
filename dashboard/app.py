"Main entry point for the dashboard app."
from pathlib import Path

import matplotlib.pyplot as plt
from shiny import App, render, ui, reactive
from ipyleaflet import (
    Map,
    GeoData,
    ImageOverlay,
)
from shinywidgets import register_widget, render_widget
import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv


# Local imports
from modules.ui import app_ui

from app_config import species_name_mapping, feature_names, app_dir

from app_utils.map import generate_basemap, layer_exists, get_layer
from app_utils.data import (
    load_training_data,
    load_partial_dependence_data,
    calculate_dependence_range,
    load_south_yorkshire,
    setup_pngs,
    load_results_df, 
)
from app_utils.cloud import generate_signed_url
from app_utils.geo import project_bbox



css_path = app_dir / "www" / "styles.css"

load_dotenv()





## Load all static app data ----------
results_df = load_results_df()
training_data_gdf = load_training_data()
partial_dependence_df = load_partial_dependence_data()
south_yorkshire = load_south_yorkshire()

dependence_range = calculate_dependence_range(partial_dependence_df)



## save the predictions to PNGs somewhere the app can GET them

png_dir = app_dir / "data" / "predictions_png"
png_dir.mkdir(exist_ok=True, parents=True)

png_urls, tif_bounds, tif_crs = setup_pngs(
)

tif_bounds = project_bbox(tif_bounds, f"EPSG:{tif_crs}", "EPSG:4326")

### App UI

main_app_ui = app_ui(
    css_path=css_path,
    species_name_mapping=species_name_mapping,
    results_df=results_df,
    
)


def server(input, output, session):

    @reactive.Calc
    def selected_results() -> pd.DataFrame:
        return results_df[
            (results_df["latin_name"] == input.species())
            & (results_df["activity_type"] == input.activity_type())
        ]


    @reactive.Calc
    def partial_dependence_range() -> pd.DataFrame:
        return dependence_range[
            (dependence_range.latin_name == input.species_mi())
            & (dependence_range.activity_type == input.activity_type_mi())
        ].copy()

    @output
    @render.data_frame
    def dependence_summary_table():
        pd_df = partial_dependence_range()
        pd_df["average"] = pd_df["average"].round(3)
        pd_df = pd_df[["feature", "average"]].sort_values("average", ascending=False)
        pd_df.feature.replace(feature_names, inplace=True)
        pd_df.rename(
            columns={"feature": "Feature", "average": "Influence Range"}, inplace=True
        )
        return pd_df

    @reactive.Calc
    def partial_dependence_df_model():
        return partial_dependence_df[
            (partial_dependence_df.latin_name == input.species_mi())
            & (partial_dependence_df.activity_type == input.activity_type_mi())
        ].copy()

    @output
    @render.plot
    def partial_dependence_plot():
        pd_df = partial_dependence_df_model()
        pd_df = pd_df[pd_df["feature"] == input.feature_mi()]
        ax = pd_df.plot(x="values", y="average")
        feature_label = feature_names[input.feature_mi()]
        ax.set_xlabel(feature_label)
        ax.set_ylabel("Effect on Habitat Suitability Score")
        # drop the legend
        ax.get_legend().remove()
        # round y axis to 2 decimal places
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.2f}"))
        return ax

    @output
    @render.ui
    def model_description():
        model_result = selected_results()

        score_mean = model_result["mean_cv_score"].values[0]
        score_std = model_result["std_cv_score"].values[0]
        n_presence = model_result["n_presence"].values[0]
        n_background = model_result["n_background"].values[0]
        folds = model_result["folds"].values[0]

        description = f"""
        This model has an accuracy of **{round(score_mean * 100, 1)}%** (+/- {round(score_std * 100, 1)})%.
        
        Species Records: {n_presence}
        """

        return ui.markdown(description)

    @reactive.Calc
    def selected_training_data() -> gpd.GeoDataFrame:
        activity_type = input.activity_type()
        latin_name = input.species()
        
        subset_gdf = training_data_gdf[
            (training_data_gdf["latin_name"] == latin_name)
        ]
        # Only filter by activity type is 'All' isn't selected
        if activity_type != "All":
            subset_gdf = subset_gdf[
                (subset_gdf["activity_type"] == activity_type)
            ]
        return subset_gdf

    @reactive.Calc
    def predictions_png_path():
        band_name = selected_results()["band_name"].values[0]
        #url =f"https://storage.googleapis.com/sygb-data/app_data/predictions_png/{band_name}.png"
        
        # encode the url replacing spaces with %20
        #url = url.replace(" ", "%20")
        #path = Path(app_dir) / "data/predictions_png/Pipistrellus pipistrellus_Foraging.png"
        #print(png_urls[band_name])

        file_path = f"app_data/predictions_png/{band_name}.png"
        url = generate_signed_url("sygb-data", file_path)
        return url

    @reactive.Calc
    def map_points():
        gdf = selected_training_data()

        #gdf = gdf[["geometry"]]
        return gdf

    ## Map ----------------------------------------------------------------------
    base_map = generate_basemap(south_yorkshire)
    register_widget("map", base_map)
    

    @output
    @render_widget
    def main_map() -> Map:
        png_url = predictions_png_path()

        if layer_exists(base_map, "HSM Predictions"):
            old_layer = get_layer(base_map, "HSM Predictions")
            base_map.remove_layer(old_layer)

        # Get the bounds of the tif
        sw_corner = [tif_bounds[0], tif_bounds[1]]
        ne_corner = [tif_bounds[2], tif_bounds[3]]
        bounds = [sw_corner, ne_corner]
        
        image_overlay = ImageOverlay(
            url=png_url,
            bounds=bounds,
            name="HSM Predictions",
            opacity=input.hsm_opacity(),
        )


        base_map.add_layer(image_overlay)


        # Check if the training data layer is already added
        layer_name = "Species Records"
        geo_data = GeoData(
            geo_dataframe=map_points(), 
            name="Species Records", 
            point_style={'color': 'black', 'radius':6, 'fillColor': '#F96E46', 'opacity':0.8, 'weight':1.3,  'fillOpacity':0.8},
            hover_style={'fillColor': '#00E8FC' , 'fillOpacity': 1},
        )

        if layer_exists(base_map, layer_name):
            old_layer = get_layer(base_map, layer_name)
            base_map.remove_layer(old_layer)
        
        base_map.add_layer(geo_data)
        

        return base_map
    

    # Model Summary --------------------------------------------------------------
    @output
    @render.data_frame
    def models_table():
        table = results_df[
            [
                "latin_name",
                "activity_type",
                "mean_cv_score",
                "std_cv_score",
                "n_presence",
                "n_background",
            ]
        ]
        table["mean_cv_score"] = (table["mean_cv_score"] * 100).round(1)
        table["std_cv_score"] = (table["std_cv_score"] * 100).round(1)
        table.rename(
            columns={
                "latin_name": "Species",
                "activity_type": "Activity Type",
                "mean_cv_score": "Accuracy (%)",
                "std_cv_score": "Accuracy Std (±%)",
                "n_presence": "Presence Points",
                "n_background": "Background Points",
            },
            inplace=True,
        )
        return table


app = App(main_app_ui, server)

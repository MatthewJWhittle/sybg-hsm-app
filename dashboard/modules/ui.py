from pathlib import Path

from shiny import ui, module
from shiny import reactive
import shinyswatch
from shinywidgets import output_widget
from app_config import feature_names

from modules.pages import about


partial_dependence_explanation = "A partial dependence plot (PDP) is a visualization tool used in habitat suitability modelling to show the relationship between a specific variable and the predicted suitability, while averaging out the effects of all other features in the model. It helps to understand how the predicted suitability depends on the feature of interest (e.g. woodland cover), regardless of the values of the other features. However, PDPs do not capture complex interactions between features, so they might not fully represent how various environmental factors together affect bat habitat suitability"


def app_ui(css_path, species_name_mapping, results_df):
    return ui.page_fluid(
        ui.include_css(css_path),
        shinyswatch.theme.minty(),
        ui.page_navbar(
            ui.nav_panel(
                "Maps",
                output_widget("main_map"),
                ui.panel_absolute(
                    ui.tags.h3("Select a Species"),
                    ui.input_selectize(
                        id="species",
                        label="",
                        choices=species_name_mapping,
                    ),
                    ui.input_selectize(
                        id="activity_type",
                        label="",
                        choices=results_df["activity_type"].unique().tolist(),
                    ),
                    ui.input_slider(
                        id="hsm_opacity",
                        label="HSM Opacity",
                        min=0,
                        max=1,
                        step=0.1,
                        value=0.8,
                    ),
                    ui.div(
                        ui.output_ui("model_description"),
                        class_="model-description-container",
                    ),
                    class_="model-selection-container",
                ),
            ),
            ui.nav_panel(
                "Model Variables",
                ui.layout_sidebar(
                    ui.panel_sidebar(
                        ui.input_selectize(
                            id="species_mi",
                            label="",
                            choices=species_name_mapping,
                        ),
                        ui.input_selectize(
                            id="activity_type_mi",
                            label="",
                            choices=results_df["activity_type"].unique().tolist(),
                        ),
                        ui.div(
                            ui.output_data_frame("dependence_summary_table"),
                            class_="dependence-summary-table-container",
                        ),
                    ),
                    ui.panel_main(
                        ui.row(
                            ui.column(
                                3,
                                # text
                                ui.tags.p("Plot Influence of:"),
                            ),
                            ui.column(
                                3,
                                ui.div(
                                    ui.input_selectize(
                                        id="feature_mi",
                                        label="",
                                        choices=feature_names,
                                    ),
                                ),
                            ),
                            ui.row(
                                ui.div(
                                    ui.output_plot("partial_dependence_plot"),
                                    class_="partial-dependence-plot-container",
                                ),
                                ui.tags.p(partial_dependence_explanation),
                            ),
                        )
                    ),
                ),
            ),
            ui.nav_panel(
                "Model Summary",
                ui.column(
                    8,  # Width
                    ui.tags.h3("Models"),
                    ui.output_data_frame("models_table"),
                    offset=2,
                    style="display: flex; flex-direction: column; align-items: center; padding-top: 20px;",
                ),
            ),
            ui.nav_spacer(),
            ui.nav_panel(
                "About",
                ui.tags.div(class_="spacer"),
                ui.div(
                    ui.column(
                        width=3,
                    ),
                    ui.column(
                        8,  # Width
                        about.markdown(),
                    ),
                    ui.column(
                        width=3,
                    ),
                    class_="about-container",
                ),
            ),
            ui.nav_panel(
                "Get in Touch!",
                ui.tags.iframe(
                    src="https://docs.google.com/forms/d/e/1FAIpQLSeOPgCJ0EC-zFzJQoLuFNh5x8OK7lQPbJyAAgdQk_twaUBtZg/viewform?embedded=true",
                    width="100%",
                    height="800px",
                    frameborder="0",
                    marginheight="0",
                    marginwidth="0",
                ),
            ),
            title="HSM: South Yorkshire Bat Group",
        ),
    )


#  <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSeOPgCJ0EC-zFzJQoLuFNh5x8OK7lQPbJyAAgdQk_twaUBtZg/viewform?embedded=true" width="640" height="936" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>

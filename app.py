# Import data from shared.py
from abloc.src.plot import plot_profile, format_profile
from abloc.src.utils import DiveProfile

import polars as pl

from shiny import App, render, ui, req, reactive
from shinywidgets import output_widget, render_widget
import great_tables.shiny as gts
from copy import copy
from pathlib import Path

css_file = Path(__file__).parent / "css" / "styles.css"

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.tags.head(
            ui.tags.link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
            )
        ),
        ui.input_slider("volume", "Bloc (L)", 10, 30, 12, step=1),
        ui.input_slider("conso", "Conso (L/min)", 10, 30, 20, step=1),
        ui.input_slider("pressure", "Pression (bar)", 0, 300, 200, step=10),
        ui.input_switch("toggle_segment", "Edit mode", False),
        ui.panel_conditional(
            "input.toggle_segment",
            ui.input_select(
                "row_select",
                "Select a profile segment",
                [],
            ),
            ui.input_slider("depth", "Depth (m)", 0, 60, 20, step=1),
            ui.input_slider("time", "Time (min)", 0, 60, 0, step=1),
            ui.input_action_button(
                "update_segment",
                "Update Segment",
                icon=ui.tags.i(class_="fa-solid fa-wand-magic-sparkles"),
            ),
        ),
    ),
    output_widget("profile_plot"),
    gts.output_gt("dive_profile"),
    ui.include_css(css_file),
    title=ui.img(
        src="https://raw.githubusercontent.com/dagousket/abloc/main/logo-readme.svg?sanitize=true",
        style="height: 50px;",
    ),
    theme=ui.Theme("yeti"),
)


def server(input, output, session):

    # create a basic initial dive profile and set up reactivity
    dp = DiveProfile(
        time=[5.0, 20.0, 10.0],
        depth=[20.0, 20.0, 0.0],
        conso=20,
        volume=12,
        pressure=200,
    )
    reactive_dp = reactive.value(dp)
    segment_list = reactive.value(dp.profile["segment"].to_list())

    @reactive.effect
    @reactive.event(input.conso, input.volume, input.pressure)
    def _():
        # copy the class to trigger reactivity
        newdp = copy(reactive_dp.get())
        newdp.conso = input.conso()
        newdp.volume = input.volume()
        newdp.pressure = input.pressure()
        newdp.update_conso()
        reactive_dp.set(newdp)

    @render_widget
    def profile_plot():
        return plot_profile(dp=reactive_dp.get())

    @reactive.effect
    @reactive.event(segment_list)
    def _():
        ui.update_select("row_select", choices=segment_list.get() + ["new segment"])

    @reactive.effect
    @reactive.event(input.row_select)
    def _():
        req(input.row_select())
        if input.row_select() == "new segment":
            ui.update_action_button(
                "update_segment",
                label="Create Segment",
                icon=ui.tags.i(class_="fa-solid fa-plus"),
            )
            return
        else:
            ui.update_action_button(
                "update_segment",
                label="Update Segment",
                icon=ui.tags.i(class_="fa-solid fa-wand-magic-sparkles"),
            )
        selected_row = reactive_dp.get().profile.filter(
            pl.col("segment") == input.row_select()
        )
        ui.update_slider("depth", value=selected_row["depth"].item())
        ui.update_slider("time", value=selected_row["time_interval"].item())

    @reactive.effect
    @reactive.event(input.update_segment)
    def _():
        req(input.row_select())
        # update the selected segment with new depth and time
        newdp = copy(reactive_dp.get())
        newdp.update_segment(
            segment=input.row_select(),
            depth=input.depth(),
            time_interval=input.time(),
        )
        newdp.update_time()
        newdp.update_conso()
        segment_list.set(newdp.profile["segment"].to_list())
        reactive_dp.set(newdp)

    @gts.render_gt
    def dive_profile():
        return format_profile(dp=reactive_dp.get())


app = App(app_ui, server)

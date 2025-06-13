# Import data from shared.py
from plot import plot_profile
from utils import format_profile, DiveProfile

from shiny import App, render, ui, req, reactive
from shinywidgets import output_widget, render_widget
import great_tables.shiny as gts
from copy import copy
from pathlib import Path

css_file = Path(__file__).parent / "css" / "styles.css"

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("volume", "Bloc (L)", 10, 30, 12, step=1),
        ui.input_slider("conso", "Conso (L/min)", 10, 30, 20, step=1),
        ui.input_slider("pressure", "Pression (bar)", 0, 300, 200, step=10),
    ),
    output_widget("profile_plot"),
    gts.output_gt("dive_profile"),
    ui.include_css(css_file),
    title="A bloc Jean  Floc'h !",
    theme=ui.Theme("yeti"),
)


def server(input, output, session):

    # create a basic initial dive profile and set up reactivity
    dp = DiveProfile(time=[0.0, 10.0, 20.0, 30.0], depth=[0.0, 20.0, 20.0, 0.0])
    reactive_dp = reactive.value(dp)

    @reactive.effect
    @reactive.event(input.conso, input.volume, input.pressure)
    def _():
        # copy the class to trigger reactivity
        newdp = copy(reactive_dp.get())
        newdp.add_litre_conso(conso=input.conso())
        newdp.add_bloc_conso(volume=input.volume(), pressure=input.pressure())
        reactive_dp.set(newdp)

    @render_widget
    def profile_plot():
        return plot_profile(df=reactive_dp.get().profile)

    @gts.render_gt
    def dive_profile():
        return format_profile(df=reactive_dp.get().profile, volume=input.volume())


app = App(app_ui, server)

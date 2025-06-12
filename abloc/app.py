# Import data from shared.py
from shared import dp

from shiny import App, render, ui, req, reactive
from shinywidgets import output_widget, render_widget
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from copy import copy

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("volume", "Bloc (L)", 10, 30, 12, step=1),
        ui.input_slider("conso", "Conso (L/min)", 10, 30, 20, step=1),
        ui.input_slider("pressure", "Pression (bar)", 0, 300, 200, step=10),
    ),
    output_widget("profile_plot"),
    ui.output_data_frame("dive_profile"),
    ui.h4("Consommation totale :"),
    ui.output_text("conso_tot"),
    title="A bloc Jean  Floc'h !",
)


def server(input, output, session):

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
        fig = px.area(data_frame=reactive_dp.get().profile, x="time", y="depth")
        fig.update_layout(
            title="Depth over Time",
            xaxis_title="Time",
            yaxis_title="Depth (m)",
        )
        fig.update_yaxes(autorange="reversed")
        return go.FigureWidget(fig)

    @render.data_frame
    def dive_profile():
        print("rendering dive profile")
        # Get the dive profile from the reactive data provider
        profile = reactive_dp.get().profile
        return render.DataGrid(profile)

    @render.text
    def conso_tot():
        conso_tot = reactive_dp.get().total_conso
        return f"{conso_tot:.2f} L"


app = App(app_ui, server)

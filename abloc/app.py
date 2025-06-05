# Import data from shared.py
from shared import df

# import function to  compute total consumption from utils.py
from utils import compute_conso_from_profile, get_total_conso

from shiny import App, render, ui, req
from shinywidgets import output_widget, render_widget
import seaborn as sns
import plotly.express as px

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("volume", "Bloc (L)", 10, 20, 12, step=1),
        ui.input_slider("conso", "Conso (L/min)", 10, 20, 17, step=1),
    ),
    output_widget("plot"),
    ui.output_data_frame("dive_profile"),
    ui.h4("Consommation totale :"),
    ui.output_text("conso_tot"),
    # ui.output_text("conso_tot", inline=True),
    title="A bloc Jean  Floc'h !",
)


def server(input, output, session):
    @render_widget
    def plot():
        fig = px.area(data_frame=df, x="time", y="depth")
        fig.update_layout(
            title="Depth over Time",
            xaxis_title="Time",
            yaxis_title="Depth (m)",
        )
        # fig.update_traces(fill="tozeroy")
        fig.update_yaxes(autorange="reversed")
        return fig

    @render.data_frame
    def dive_profile():
        return render.DataGrid(df)

    @render.text
    def conso_tot():
        req(input.conso)
        conso_tot = get_total_conso(compute_conso_from_profile(df, input.conso()))
        return f"{conso_tot:.2f} L"


app = App(app_ui, server)

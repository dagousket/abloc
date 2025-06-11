# Import data from shared.py
from shared import df

from shiny import App, render, ui, req
from shinywidgets import output_widget, render_widget
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("volume", "Bloc (L)", 10, 30, 12, step=1),
        ui.input_slider("conso", "Conso (L/min)", 10, 30, 20, step=1),
    ),
    output_widget("profile_plot"),
    ui.output_data_frame("dive_profile"),
    ui.h4("Consommation totale :"),
    ui.output_text("conso_tot"),
    # ui.output_text("conso_tot", inline=True),
    title="A bloc Jean  Floc'h !",
)


def server(input, output, session):
    @render_widget
    def profile_plot():
        fig = px.area(data_frame=df.profile, x="time", y="depth")
        fig.update_layout(
            title="Depth over Time",
            xaxis_title="Time",
            yaxis_title="Depth (m)",
        )
        # fig.update_traces(fill="tozeroy")
        fig.update_yaxes(autorange="reversed")
        return go.FigureWidget(fig)

    @render.data_frame
    def dive_profile():
        return render.DataGrid(df.profile)

    @render.text
    def conso_tot():
        req(input.conso)
        conso_tot = df.total_conso
        return f"{conso_tot:.2f} L"


app = App(app_ui, server)

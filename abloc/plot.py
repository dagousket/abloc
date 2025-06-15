import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import DiveProfile


def plot_profile(
    dp: DiveProfile, x: str = "time", y1: str = "depth", y2: str = "bar_remaining"
) -> go.FigureWidget:
    """
    Create the Dive Profile plot.
    Parameters
    ----------
    dp : DiveProfile
        A DiveProfile object containing the dive data.
    x : str
        Column name for the x-axis (default is "time").
    y1 : str
        Column name for the first y-axis (default is "depth").
    y2 : str
        Column name for the second y-axis (default is "bar_remaining").
    Returns
    -------
    go.FigureWidget
        A Plotly FigureWidget containing the dive profile plot.
    """
    # Add initial time point to dataframe
    initial_state = pl.DataFrame(
        {
            "time": [0.0],
            "depth": [0.0],
            "bar_remaining": float(dp.pressure),
        }
    )
    df = pl.concat([initial_state, dp.profile], how="diagonal_relaxed")

    # Record max values for plot range
    max_depth = df.select(pl.max(y1)).item()
    max_bar = df.select(pl.max(y2)).item()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=df[x], y=df[y1], name="depth", line=dict(color="navy")),
        secondary_y=False,
    )

    fig.update_traces(fill="tozeroy", line_color="rgba(0,100,80,0.2)")

    fig.add_trace(
        go.Scatter(x=df[x], y=df[y2], name="bloc", line=dict(color="navy")),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(title_text="Dive Profile", template="plotly_white")

    # Set x-axis title
    fig.update_xaxes(title_text="<b>Dive time</b> (min)")

    # Set y-axes titles
    fig.update_yaxes(
        title_text="<b>Depth</b> (m)",
        range=[max_depth, 0],
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="<b>Bloc pressure</b> (bar)",
        range=[0, max_bar],
        secondary_y=True,
    )

    return go.FigureWidget(fig)

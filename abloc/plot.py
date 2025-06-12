import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_profile(
    df: pl.DataFrame, x: str = "time", y1: str = "depth", y2: str = "bar_remining"
) -> go.FigureWidget:
    """
    Create a simple plot with two traces.
    This function is a placeholder for testing purposes.
    """
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

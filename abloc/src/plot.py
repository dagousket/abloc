import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from great_tables import GT, html
from importlib_resources import files
from .utils import DiveProfile


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
    mean_depth = df.select(pl.mean(y1)).item()

    # Record middle point for time interval
    df = df.with_columns(
        mid_interval=pl.col("time") - 0.5 * pl.col("time_interval"),
        mid_pressure=pl.col("bar_remaining")
        + 0.5 * (pl.col("bar_remaining").shift(n=1) - pl.col("bar_remaining"))
        - 10,
    )

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=df[x], y=df[y1], name="Depth", line=dict(color="navy")),
        secondary_y=False,
    )

    fig.update_traces(fill="tozeroy", line_color="rgba(0,100,80,0.2)")

    fig.add_trace(
        go.Scatter(x=df[x], y=df[y2], name="Bloc pressure", line=dict(color="navy")),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=df["mid_interval"],
            y=df["mid_pressure"],
            mode="text",
            name="Segment",
            text=df["segment"],
            textposition="bottom center",
            textfont=dict(size=18, color="navy", weight=900),
        ),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title=dict(text="Dive Profile", font=dict(size=20, weight=900)),
        template="plotly_white",
    )

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


def format_profile(dp: DiveProfile) -> GT:
    """
    Format the dive profile DataFrame for display.

    Parameters:
    - df: DataFrame containing the dive profile.

    Returns:
    - Formatted DataFrame with rounded values.
    """
    # Add starting point
    initial_state = pl.DataFrame(
        {
            "time": [0.0],
            "time_interval": [0.0],
            "depth": [0.0],
            "bar_remaining": [float(dp.pressure)],
            "conso_remaining": [float(dp.volume * dp.pressure)],
            "conso_totale": [0.0],
            "segment": ["Start"],
            "conso_per_min": [None],
        }
    )
    df = pl.concat([initial_state, dp.profile], how="diagonal_relaxed")

    # Assess direction (down-stable-up)
    df = df.with_columns(
        pl.when(pl.col("depth") > pl.col("depth").shift(1))
        .then(pl.lit("down"))
        .when(pl.col("depth") < pl.col("depth").shift(1))
        .then(pl.lit("up"))
        .otherwise(pl.lit("stable"))
        .alias("direction"),
        speed=(
            (pl.col("depth").shift(1) - pl.col("depth")) / pl.col("time_interval")
        ).round(2),
    )

    required_columns = {"conso_totale", "conso_remaining", "bar_remaining"}
    table_output = df.with_columns(
        pl.col(required_columns).clip(lower_bound=0).round(0)
    ).select(
        [
            "segment",
            "direction",
            "speed",
            "time_interval",
            "depth",
            "bar_remaining",
            "conso_remaining",
            "conso_per_min",
        ]
    )
    table_output = (
        GT(table_output)
        .tab_header(title="Dive Profile Summary")
        .cols_move_to_start(
            columns=[
                "segment",
                "direction",
                "speed",
                "time_interval",
                "depth",
                "conso_per_min",
                "conso_remaining",
                "bar_remaining",
            ]
        )
        .cols_label(
            segment=html("<b>Segment</b>"),
            direction=html("<b>Direction</b>"),
            speed=html("<b>Speed</b> (m/min)"),
            time_interval=html("<b>Time</b> (min)"),
            depth=html("<b>Depth</b> (m)"),
            conso_per_min=html("<b>Air consumption</b> (L/min)"),
            conso_remaining=html("<b>Air remaining</b> (L)"),
            bar_remaining=html("<b>Pressure remaining</b> (bar)"),
        )
        .fmt_image(
            columns="direction",
            path=files("abloc") / "src/img",
            file_pattern="logo-diver-{}.svg",
        )
        .data_color(
            columns=["bar_remaining"],
            palette=["firebrick", "lightcoral"],
            domain=[0, 50],
            na_color="white",
        )
        .data_color(
            columns=["conso_remaining"],
            palette=["firebrick", "lightcoral"],
            domain=[0, 50 * dp.volume],
            na_color="white",
        )
        .data_color(
            columns=["speed"],
            palette=["firebrick", "lightcoral"],
            domain=[10, 30],
            na_color="white",
        )
        .sub_missing(missing_text="")
    )
    return table_output

import pytest

from abloc.src import utils
from abloc.src import plot
import plotly.graph_objects as go
import polars as pl


def test_plot():
    dummy_dp = utils.DiveProfile(
        time=[5.0, 20.0, 10.0],
        depth=[20.0, 20.0, 0.0],
        conso=[20, 20, 20],
        volume=12,
        pressure=200,
    )
    dummy_dp.update_conso()

    # Test if the plot function returns a figure object
    fig = plot.plot_profile(dp=dummy_dp, x="time", y1="depth", y2="bar_remaining")
    assert isinstance(fig, go.FigureWidget)
    # Test if the figure has the expected number of traces
    data = fig.data
    assert len(data) == 3
    assert data[0].name == "Depth"
    assert data[1].name == "Bloc pressure"
    assert data[2].name == "Segment"
    # Test if the x-axis and y-axes titles are set correctly
    assert fig.layout.xaxis.title.text == "<b>Dive time</b> (min)"
    assert fig.layout.yaxis.title.text == "<b>Depth</b> (m)"
    assert fig.layout.yaxis2.title.text == "<b>Bloc pressure</b> (bar)"
    # Test if the figure title is set correctly
    assert fig.layout.title.text == "Dive Profile"
    # Test if the y-axis ranges are set correctly
    assert fig.layout.yaxis.range == (20.0, 0)  # Depth should be descending
    assert fig.layout.yaxis2.range == (0, 200.0)  # Bloc pressure should be ascending

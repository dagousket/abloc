import pytest

from abloc import utils
from abloc import plot
import plotly.graph_objects as go
import polars as pl


def test_plot():
    dummy_dp = utils.DiveProfile(
        time=[5.0, 20.0, 10.0],
        depth=[20.0, 20.0, 0.0],
        conso=20,
        volume=12,
        pressure=200,
    )
    dummy_dp.update_conso()

    # Test if the plot function returns a figure object
    fig = plot.plot_profile(
        df=dummy_dp.profile, x="time", y1="depth", y2="bar_remaining"
    )
    assert isinstance(fig, go.FigureWidget)
    # Test if the figure has the expected number of traces
    data = fig.data
    assert len(data) == 2
    assert data[0].name == "depth"
    assert data[1].name == "bloc"
    # Test if the x-axis and y-axes titles are set correctly
    assert fig.layout.xaxis.title.text == "<b>Dive time</b> (min)"
    assert fig.layout.yaxis.title.text == "<b>Depth</b> (m)"
    assert fig.layout.yaxis2.title.text == "<b>Bloc pressure</b> (bar)"
    # Test if the figure title is set correctly
    assert fig.layout.title.text == "Dive Profile"
    # Test if the y-axis ranges are set correctly
    assert fig.layout.yaxis.range == (20.0, 0)  # Depth should be descending
    assert fig.layout.yaxis2.range == (0, 200.0)  # Bloc pressure should be ascending

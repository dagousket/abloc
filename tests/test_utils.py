import pytest
import polars as pl
import great_tables as gt
from abloc.src import utils


def test_diveprofile_class():
    dp = utils.DiveProfile(time=[5, 20, 10], depth=[20, 20, 0])
    assert isinstance(dp, utils.DiveProfile), "DiveProfile class is correct"
    assert isinstance(dp.profile, utils.pl.DataFrame), "Profile is a polars DataFrame"
    assert dp.profile.shape == (3, 4), "Profile has 3 rows and 2 columns"
    assert dp.profile.columns == [
        "time_interval",
        "depth",
        "segment",
        "time",
    ], "Profile has correct columns names"
    assert dp.profile["time"].to_list() == [5, 25, 35], "Time column is correct"
    assert dp.profile["depth"].to_list() == [20, 20, 0], "Depth column is correct"


def test_update_conso():
    dp = utils.DiveProfile(
        time=[5, 20, 10], depth=[20, 20, 0], conso=20, volume=12, pressure=200
    )
    # no total conso before adding conso
    with pytest.raises(ValueError):
        dp.total_conso
    dp.update_conso()
    assert "conso" in dp.profile.columns, "Conso column is added to profile"
    assert dp.profile["conso"].to_list() == [
        200.0,
        1200.0,
        400.0,
    ], "Conso values are correct"
    assert (
        dp.total_conso == 1800.0
    ), "Total conso is correctly computed after adding conso"
    assert "conso_remaining" in dp.profile.columns, "conso_remaining column is added"
    assert "bar_remaining" in dp.profile.columns, "bar_remaining column is added"
    assert dp.profile["conso_remaining"].to_list() == [
        2200.0,
        1000.0,
        600.0,
    ], "conso_totale values are correct"
    assert dp.profile["bar_remaining"].round().to_list() == [
        183.0,
        83.0,
        50.0,
    ], "bar_remaining values are correct"


def test_update_time():
    dp = utils.DiveProfile(
        time=[5, 20, 10], depth=[20, 20, 0], conso=20, volume=12, pressure=200
    )
    # no total time before updating time
    dp.profile = dp.profile.with_columns(time_interval=pl.Series([5, 20, 30]))
    assert dp.profile["time"].to_list() == [5, 25, 35], "Initial time is correct"
    dp.update_time()
    assert dp.profile["time"].to_list() == [
        5,
        25,
        55,
    ], "Time column is updated correctly"


def test_update_segment():
    dp = utils.DiveProfile(
        time=[5, 20, 10], depth=[20, 20, 0], conso=20, volume=12, pressure=200
    )
    assert dp.profile.filter(pl.col("segment") == "B").row(0) == (
        20,
        20,
        "B",
        25,
    ), "Initial B segment is correct"
    dp.update_segment(segment="B", time_interval=30, depth=10)
    assert dp.profile.filter(pl.col("segment") == "B").row(0) == (
        30,
        10,
        "B",
        25,
    ), "New B segment is correct"


def test_format_profile():
    dp = utils.DiveProfile(
        time=[5, 20, 10], depth=[20, 20, 0], conso=20, volume=12, pressure=200
    )
    with pytest.raises(ValueError):
        utils.format_profile(dp)
    dp.update_conso()
    formatted_profile = utils.format_profile(dp)
    assert isinstance(formatted_profile, gt.GT), "Formatted profile is a GT"
    assert isinstance(
        formatted_profile._tbl_data, pl.DataFrame
    ), "GT data is a polars DataFrame"


def test_missing_columns():
    df = pl.DataFrame(
        {
            "time_interval": [5, 20, 10],
            "depth": [20, 20, 0],
            "segment": ["A", "B", "C"],
        }
    )
    with pytest.raises(ValueError):
        utils.compute_remaining_conso(df, volume=12, pressure=200)

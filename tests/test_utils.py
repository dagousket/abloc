import pytest
import polars as pl

from abloc import utils


def test_diveprofile_class():
    dp = utils.DiveProfile(time=[0, 1, 2], depth=[0, 10, 20])
    assert isinstance(dp, utils.DiveProfile), "DiveProfile class is correct"
    assert isinstance(dp.profile, utils.pl.DataFrame), "Profile is a polars DataFrame"
    assert dp.profile.shape == (3, 2), "Profile has 3 rows and 2 columns"
    assert dp.profile.columns == ["time", "depth"], "Profile has correct columns names"
    assert dp.profile["time"].to_list() == [0, 1, 2], "Time column is correct"
    assert dp.profile["depth"].to_list() == [0, 10, 20], "Depth column is correct"


def test_add_litre_conso_and_total_conso():
    dp = utils.DiveProfile(time=[0, 1, 2], depth=[0, 10, 20])
    # no total conso before adding conso
    with pytest.raises(ValueError):
        dp.total_conso
    dp.add_litre_conso(conso=10.0)
    assert "conso" in dp.profile.columns, "Conso column is added to profile"
    assert dp.profile["conso"].to_list() == [
        0.0,
        15.0,
        25.0,
    ], "Conso values are correct"
    assert (
        dp.total_conso == 40.0
    ), "Total conso is correctly computed after adding conso"


def test_add_bloc_conso():
    dp = utils.DiveProfile(time=[0, 1, 2], depth=[0, 10, 20])
    dp.add_litre_conso(conso=10.0)  # Add some consumption to the profile
    dp.add_bloc_conso(volume=10.0, pressure=100.0)  # Example volume and pressure
    assert "conso_remaining" in dp.profile.columns, "conso_remaining column is added"
    assert "bar_remaining" in dp.profile.columns, "bar_remaining column is added"
    assert dp.profile["conso_remaining"].to_list() == [
        1000.0,
        985.0,
        960.0,
    ], "conso_totale values are correct"
    assert dp.profile["bar_remaining"].to_list() == [
        100.0,
        98.5,
        96,
    ], "bar_remaining values are correct"


def test_format_profile():
    dp = utils.DiveProfile(time=[0, 1, 2], depth=[0, 10, 20])
    dp.add_litre_conso(conso=10.0)
    dp.add_bloc_conso(volume=10.0, pressure=1.0)
    formatted_profile = utils.format_profile(dp.profile)
    assert isinstance(
        formatted_profile, pl.DataFrame
    ), "Formatted profile a polars DataFrame"
    assert formatted_profile["conso_remaining"].to_list() == [
        10.0,
        0.0,
        0.0,
    ], "Formatted conso_remaining is not going under 0"
    assert formatted_profile["bar_remaining"].to_list() == [
        1.0,
        0.0,
        0.0,
    ], "Formatted bar_remaining is not going under 0"

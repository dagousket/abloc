import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class DiveProfile:

    def __init__(self, time: list[float], depth: list[float]):
        """
        Initialize a DiveProfile instance.
        Parameters:
        - time: Time in minutes.
        - depth: Depth in meters.
        """
        self.profile = pl.DataFrame(
            {
                "time": time,  # (minutes),
                "depth": depth,  # (meters)
            }
        )

    @property
    def total_conso(self) -> float:
        """
        Compute the total air consumption from the dive profile.

        Returns:
        - Total air consumption in liters.
        """
        return get_total_conso(self.profile)

    def add_litre_conso(self, conso: float) -> None:
        """
        Add the air consumption to the dive profile.
        Parameters:
        - conso: Consumption rate in liters per minute.
        Returns:
        - None : Update dive profile with the new consumption added.
        """
        self.profile = compute_conso_from_profile(self.profile, conso)

    def add_bloc_conso(self, volume: float, pressure: float) -> None:
        # Ensure the profile has conso_totale and bar_remining columns
        if "conso_totale" not in self.profile.columns:
            raise ValueError(
                "Profile must have 'conso_totale' column to add bloc conso."
            )
        self.profile = compute_remaining_conso(self.profile, volume, pressure)


def compute_conso_from_profile(df: pl.DataFrame, conso: float) -> pl.DataFrame:
    """
    Compute the air consumption based on the dive profile.

    Parameters:
    - df: DataFrame containing the dive profile with 'time' and 'depth' columns.
    - conso: Consumption rate in liters per minute.

    Returns:
    - polars dataframe with conso and cumulative conso columns.
    """
    # Compute the time relative to pressure (in bar)
    # result is expressed in surface time equivalent (in minutes)

    df = (
        df.with_columns(
            lag_time=pl.col("time") - pl.col("time").shift(fill_value=0),
            init_bar=(pl.col("depth").shift(fill_value=0) / 10) + 1,
            bar=(pl.col("depth") / 10) + 1,
        )
        .with_columns(
            trpz_area=(pl.col("bar") + pl.col("init_bar")) * pl.col("lag_time") / 2
        )
        .with_columns(conso=pl.col("trpz_area") * conso)
        .select(
            pl.col("time"),
            pl.col("depth"),
            pl.col("conso"),
            pl.col("conso").cum_sum().alias("conso_totale"),
        )
    )
    return df


def get_total_conso(df: pl.DataFrame) -> float:
    """
    Compute the total air consumption from the dive profile.

    Parameters:
    - df: DataFrame containing the dive profile with conso_totale columns.

    Returns:
    - Total air consumption in liters.
    """
    return df.select(pl.last("conso_totale")).item()


def compute_remaining_conso(
    df: pl.DataFrame, volume: float, pressure: float
) -> pl.DataFrame:
    """
    Add the air consumption in bar to the dive profile.

    Parameters:
    - df: DataFrame containing the dive profile with conso_totale columns.
    - volume: volume of the tank.
    - pressure: pressure of the tank in bar.

    Returns:
    - polars dataframe with conso_remaining and bar_remining columns.
    """
    # Create a new row with the last time and depth, and the new conso
    df = df.with_columns(
        conso_remaining=((volume * pressure) - pl.col("conso_totale")),
        bar_remaining=(pressure - (pl.col("conso_totale") / volume)),
    )

    return df


def format_profile(df: pl.DataFrame) -> pl.DataFrame:
    """
    Format the dive profile DataFrame for display.

    Parameters:
    - df: DataFrame containing the dive profile.

    Returns:
    - Formatted DataFrame with rounded values.
    """
    return df.with_columns(
        pl.col("conso_totale", "conso_remaining", "bar_remaining").round(0)
    ).with_columns(pl.col("conso_remaining", "bar_remaining").clip(lower_bound=0))

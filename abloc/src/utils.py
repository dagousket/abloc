import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from string import ascii_uppercase


class DiveProfile:

    def __init__(
        self,
        time: list[float],
        depth: list[float],
        conso: list[float],
        volume: float = 12.0,
        pressure: float = 200.0,
    ):
        """
        Initialize a DiveProfile instance.
        Parameters:
        - time: Time interval in minutes.
        - depth: Depth in meters.
        Returns:
        - None : Initializes the dive profile with time, depth, and segment labels.
        """
        self.profile = pl.DataFrame(
            {
                "time_interval": time,  # (minutes),
                "depth": depth,  # (meters),
                "conso_per_min": conso,  # (liters per minute)
                "segment": list(ascii_uppercase[: len(time)]),  # Segment labels
            }
        ).with_columns(time=pl.col("time_interval").cum_sum())
        self.volume = volume  # Block volume in liters
        self.pressure = pressure  # Pressure in bar

    @property
    def total_conso(self) -> float:
        """
        Compute the total air consumption from the dive profile.

        Returns:
        - Total air consumption in liters.
        """
        return get_total_conso(self.profile)

    def update_conso(self) -> None:
        """
        Update the dive profile with air consumption and remaining air.
        Parameters:
        - None
        Returns:
        - None : Updates the profile with conso and remaining conso.
        """
        self.profile = compute_conso_from_profile(self.profile)
        self.profile = compute_remaining_conso(self.profile, self.volume, self.pressure)

    def update_time(self) -> None:
        """
        Update the time intervals of the dive profile.
        Returns:
        - None : Update the time intervals in the profile.
        """
        self.profile = self.profile.with_columns(time=pl.col("time_interval").cum_sum())

    def update_segment(
        self, segment: str, time_interval: float, depth: float, conso: float
    ) -> None:
        """
        Update a specific segment of the dive profile.
        Parameters:
        - segment: Segment label to update.
        - time_interval: New time in minutes for the segment.
        - depth: New depth in meters for the segment.
        - conso: New consumption rate in liters per minute for the segment.
        Returns:
        - None : Update the specified segment with new time and depth.
        """
        self.profile = edit_segment_time_depth(
            self.profile, segment, time_interval, depth, conso
        )


def compute_conso_from_profile(df: pl.DataFrame) -> pl.DataFrame:
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
            init_bar=(pl.col("depth").shift(fill_value=0) / 10) + 1,
            bar=(pl.col("depth") / 10) + 1,
        )
        .with_columns(
            trpz_area=(pl.col("bar") + pl.col("init_bar")) * pl.col("time_interval") / 2
        )
        .with_columns(conso=pl.col("trpz_area") * pl.col("conso_per_min"))
        .select(
            pl.col("segment"),
            pl.col("time"),
            pl.col("time_interval"),
            pl.col("depth"),
            pl.col("conso"),
            pl.col("conso_per_min"),
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
    # Ensure the profile has conso_totale and bar_remining columns
    if "conso_totale" not in df.columns:
        raise ValueError("Profile must have 'conso_totale' column to get total conso.")
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
    if "conso_totale" not in df.columns:
        raise ValueError("Profile must have 'conso_totale' column to add bloc conso.")

    # Create a new row with the last time and depth, and the new conso
    df = df.with_columns(
        conso_remaining=((volume * pressure) - pl.col("conso_totale")),
        bar_remaining=(pressure - (pl.col("conso_totale") / volume)),
    )

    return df


def edit_segment_time_depth(
    df: pl.DataFrame, segment: str, time_interval: float, depth: float, conso: float
) -> pl.DataFrame:
    """
    Update a specific segment of the dive profile.
    Parameters:
    - segment: Segment label to update.
    - time_interval: New time in minutes for the segment.
    - depth: New depth in meters for the segment.
    - conso: New consumption rate in liters per minute for the segment.
    Returns:
    - None : Update the specified segment with new time and depth.
    """
    if segment in df["segment"].to_list():
        df = df.with_columns(
            pl.when(pl.col("segment") == segment)
            .then(pl.lit(time_interval))
            .otherwise("time_interval")
            .alias("time_interval"),
            pl.when(pl.col("segment") == segment)
            .then(pl.lit(depth))
            .otherwise("depth")
            .alias("depth"),
            pl.when(pl.col("segment") == segment)
            .then(pl.lit(conso))
            .otherwise("conso_per_min")
            .alias("conso_per_min"),
        )
    else:
        # If the segment does not exist, create a new one
        new_segment = pl.DataFrame(
            {
                "time_interval": [time_interval],
                "depth": [depth],
                "segment": [ascii_uppercase[len(df)]],  # New segment label
                "conso_per_min": [conso],  # New consumption rate
            }
        )
        df = pl.concat([df, new_segment], how="diagonal_relaxed")

    return df

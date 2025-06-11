import polars as pl


class DiveProfile:

    def __init__(self, time: list[float], depth: list[float], conso: float = 20.0):
        """
        Initialize a DiveProfile instance.
        Parameters:
        - time: Time in minutes.
        - depth: Depth in meters.
        - conso: Consumption rate in liters per minute (default is 20.0).
        """
        profile = pl.DataFrame(
            {
                "time": time,  # (minutes),
                "depth": depth,  # (meters)
            }
        )
        self.profile = compute_conso_from_profile(profile, conso)

    @property
    def total_conso(self) -> float:
        """
        Compute the total air consumption from the dive profile.

        Returns:
        - Total air consumption in liters.
        """
        return get_total_conso(self.profile)


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

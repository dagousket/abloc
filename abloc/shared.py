import polars as pl

# create a basic initial dive profile
df = pl.DataFrame(
    {
        "time": [0, 10, 20, 30],  # (minutes),
        "depth": [0, 20, 20, 0],  # (meters)
    }
)

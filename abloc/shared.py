import polars as pl
from utils import DiveProfile

# create a basic initial dive profile
dp = DiveProfile(time=[0.0, 10.0, 20.0, 30.0], depth=[0.0, 20.0, 20.0, 0.0])

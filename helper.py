import tensorflow as tf
from ray.data.preprocessors import (
    BatchMapper,
    Chain,
    OneHotEncoder,
    SimpleImputer,
)

import numpy as np
import pandas as pd

INPUT = "input"
LABEL = "is_big_tip"

# Note that `INPUT_SIZE` here is corresponding to the output dimension
# of the previously defined processing steps.
# This is used to specify the input shape of Keras model.
INPUT_SIZE = 120
# The training batch size. Based on `NUM_WORKERS`, each worker
# will get its own share of this batch size. For example, if
# `NUM_WORKERS = 2`, each worker will work on 4 samples per batch.
BATCH_SIZE = 8
# Number of epoch. Adjust it based on how quickly you want the run to be.
EPOCH = 1
# Number of training workers.
# Adjust this accordingly based on the resources you have!
NUM_WORKERS = 2


def get_preprocessor():
    """Construct a chain of preprocessors."""
    imputer1 = SimpleImputer(["dropoff_census_tract"],
                             strategy="most_frequent")
    imputer2 = SimpleImputer(
        ["pickup_community_area", "dropoff_community_area"],
        strategy="most_frequent",
    )
    imputer3 = SimpleImputer(["payment_type"], strategy="most_frequent")
    imputer4 = SimpleImputer(["company"], strategy="most_frequent")
    imputer5 = SimpleImputer(
        ["trip_start_timestamp", "trip_miles", "trip_seconds"], strategy="mean"
    )

    ohe = OneHotEncoder(
        columns=[
            "trip_start_hour",
            "trip_start_day",
            "trip_start_month",
            "dropoff_census_tract",
            "pickup_community_area",
            "dropoff_community_area",
            "payment_type",
            "company",
        ],
        max_categories={
            "dropoff_census_tract": 25,
            "pickup_community_area": 20,
            "dropoff_community_area": 20,
            "payment_type": 2,
            "company": 7,
        },
    )

    def batch_mapper_fn(df):
        df["trip_start_year"] = pd.to_datetime(
            df["trip_start_timestamp"], unit="s"
        ).dt.year
        df = df.drop(["trip_start_timestamp"], axis=1)
        return df

    def concat_for_tensor(dataframe):
        from ray.data.extensions import TensorArray

        result = {}
        feature_cols = [col for col in dataframe.columns if col != LABEL]
        result[INPUT] = TensorArray(
            dataframe[feature_cols].to_numpy(dtype=np.float32))
        if LABEL in dataframe.columns:
            result[LABEL] = dataframe[LABEL]
        return pd.DataFrame(result)

    chained_pp = Chain(
        imputer1,
        imputer2,
        imputer3,
        imputer4,
        imputer5,
        ohe,
        BatchMapper(batch_mapper_fn, batch_format="pandas"),
        BatchMapper(concat_for_tensor, batch_format="pandas"),
    )
    return chained_pp


def build_model():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.Input(shape=(INPUT_SIZE,)))
    model.add(tf.keras.layers.Dense(50, activation="relu"))
    model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
    return model

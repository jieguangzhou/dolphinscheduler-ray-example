import pandas as pd
import os
from helper import LABEL


def get_data() -> pd.DataFrame:
    """Fetch the taxi fare data to work on."""
    _data = pd.read_csv("https://raw.githubusercontent.com/tensorflow/tfx/master/"
                        "tfx/examples/chicago_taxi_pipeline/data/simple/data.csv")
    _data[LABEL] = _data["tips"] / _data["fare"] > 0.2
    # We drop some columns here for the sake of simplicity.
    return _data.drop(
        [
            "tips",
            "fare",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_latitude",
            "pickup_longitude",
            "pickup_census_tract",
        ],
        axis=1,
    )


data = get_data()
print(data.head(5))

tmp_dir = '/tmp/ray-example/data/'

os.makedirs(tmp_dir, exist_ok=True)

data_path = os.path.join(tmp_dir, "data.csv")

data.to_csv(data_path, index=False)
print('${setValue(data_path=%s)}' % data_path)

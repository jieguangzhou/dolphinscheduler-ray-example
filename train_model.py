import pickle
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple
import numpy as np

import ray
from ray.air.config import ScalingConfig
from ray.train.tensorflow import TensorflowTrainer
from ray.train.tensorflow import TensorflowCheckpoint
from ray.air import session
import tensorflow as tf
from helper import build_model, get_preprocessor, NUM_WORKERS, EPOCH, INPUT, LABEL, BATCH_SIZE

data_path = "/tmp/ray-example/data/data.csv"  # $PARAM:
batch_size = BATCH_SIZE  # $PARAM:
n_epoch = EPOCH  # $PARAM: epoch

ray.init(address="auto")

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


def split_data(data: pd.DataFrame) -> Tuple[ray.data.Dataset, pd.DataFrame, np.array]:
    """Split the data in a stratified way.

    Returns:
        A tuple containing train dataset, test data and test label.
    """
    # There is a native offering in Ray Dataset for split as well.
    # However, supporting stratification is a TODO there. So use
    # scikit-learn equivalent here.
    train_data, test_data = train_test_split(
        data, stratify=data[[LABEL]], random_state=1113
    )
    _train_ds = ray.data.from_pandas(train_data)
    _test_label = test_data[LABEL].values
    _test_df = test_data.drop([LABEL], axis=1)
    return _train_ds, _test_df, _test_label


data = get_data()

tmp_dir = '/tmp/ray-example/data/'

os.makedirs(tmp_dir, exist_ok=True)

data_path = os.path.join(tmp_dir, "data.csv")

data.to_csv(data_path, index=False)
print('${setValue(data_path=%s)}' % data_path)

train_ds, test_df, test_label = split_data(data)
print(
    f"There are {train_ds.count()} samples for training and {test_df.shape[0]} samples for testing."
)

save_path = os.path.join(os.path.dirname(data_path), "dataset.pkl")

datas = {
    "train_ds": train_ds,
    "test_df": test_df,
    "test_label": test_label,

}

with open(save_path, "wb") as f:
    pickle.dump(datas, f)

print('${setValue(dataset_path=%s)}' % save_path)


def train_loop_per_worker():
    dataset_shard = session.get_dataset_shard("train")

    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    with strategy.scope():
        model = build_model()
        model.compile(
            loss="binary_crossentropy",
            optimizer="adam",
            metrics=["accuracy"],
        )

    for epoch in range(n_epoch):
        tf_dataset = dataset_shard.to_tf(
            feature_columns=INPUT,
            label_columns=LABEL,
            batch_size=batch_size,
            drop_last=True,
        )

        model.fit(tf_dataset, verbose=0)
        # This saves checkpoint in a way that can be used by Ray Serve coherently.
        session.report(
            {},
            checkpoint=TensorflowCheckpoint.from_model(model),
        )


trainer = TensorflowTrainer(
    train_loop_per_worker=train_loop_per_worker,
    scaling_config=ScalingConfig(num_workers=NUM_WORKERS),
    datasets={"train": train_ds},
    preprocessor=get_preprocessor(),
)
result = trainer.fit()

print(result.metrics)
print(result.checkpoint)

checkpoint_path = os.path.abspath(os.path.join(
    os.path.dirname(data_path), '..', "checkpoint.bin"))
with open(checkpoint_path, 'wb') as w_f:
    w_f.write(result.checkpoint.to_bytes())

print('${setValue(checkpoint_path=%s)}' % checkpoint_path)

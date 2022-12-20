import json
import pandas as pd
import requests
import numpy as np
import pickle

NUM_SERVE_REQUESTS = 10

dataset_path = '/tmp/ray-example/data/dataset.pkl'
endpoint_uri = "http://localhost:8000"

dataset = pickle.load(open(dataset_path, 'rb'))

test_df = dataset['test_df']
test_label = dataset['test_label']


def send_requests(df: pd.DataFrame, label: np.array):
    for i in range(NUM_SERVE_REQUESTS):
        one_row = df.iloc[[i]].to_dict()
        serve_result = requests.post(
            endpoint_uri,
            data=json.dumps(one_row),
            headers={"Content-Type": "application/json"},
        ).json()
        print(
            f"request{i} prediction: {serve_result[0]['predictions']} "
            f"- label: {str(label[i])}"
        )


send_requests(test_df, test_label)

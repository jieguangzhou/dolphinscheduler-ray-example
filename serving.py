import ray
from ray.serve import PredictorDeployment
from ray.train.tensorflow import TensorflowPredictor
from ray.air.checkpoint import Checkpoint
from ray import serve
from fastapi import Request
from helper import build_model
import pandas as pd


async def dataframe_adapter(request: Request):
    """Serve HTTP Adapter that reads JSON and converts to pandas DataFrame."""
    content = await request.json()
    return pd.DataFrame.from_dict(content)


def serve_model(checkpoint: Checkpoint, model_definition, adapter, name="Model") -> str:
    """Expose a serve endpoint.

    Returns:
        serve URL.
    """
    serve.run(
        PredictorDeployment.options(name=name).bind(
            TensorflowPredictor,
            checkpoint,
            batching_params=dict(max_batch_size=2, batch_wait_timeout_s=5),
            model_definition=model_definition,
            http_adapter=adapter,
        )
    )
    return f"http://localhost:8000/"


# Generally speaking, training and serving are done in totally different ray clusters.
# To simulate that, let's shutdown the old ray cluster in preparation for serving.

checkpoint_path = "/tmp/ray-example/checkpoint.bin"

with open(checkpoint_path, "rb") as r_f:
    checkpoint = Checkpoint.from_bytes(r_f.read())
endpoint_uri = serve_model(checkpoint, build_model, dataframe_adapter)
print(endpoint_uri)

from pydolphinscheduler.tasks import Python, Shell
from pydolphinscheduler.core.workflow import Workflow
from pydolphinscheduler.core.resource import Resource

CONVERT_TAG = "# $PARAM:"


# load script to dolphinscheduler, and convert special param with CONVERT_TAG
def load_script(path):
    with open(path, 'r') as f:
        script_lines = []
        for line in f:
            if CONVERT_TAG not in line:
                script_lines.append(line)
                continue

            base_line, annotation = line.rstrip().split(CONVERT_TAG)
            param_name, param_value = base_line.split("=")
            param_value = param_value.strip()

            annotation = annotation or param_name.strip()
            annotation = "${%s}" % annotation.strip()

            if param_value.startswith('"') and param_value.endswith('"'):
                annotation = "\"" + annotation + "\""

            new_line = param_name + "= " + annotation + "\n"
            script_lines.append("# original: " + line)
            script_lines.append(new_line)

        script = "".join(script_lines)
        return script


def load_resource(file_name):
    with open(file_name, 'r') as f:
        content = f.read()

    resource = Resource(name=file_name, content=content)
    return resource


resource_helper = load_resource("helper.py")

with Workflow(
    name="training",
    resource_list=[
        resource_helper
    ],
    param={
        "train_ray_address": "auto",
        "deploy_ray_address": "auto",
    }
) as pd:

    # dowanload data
    task_get_data = Python(
        name="get_data",
        definition=load_script("get_data.py"),
        resource_list=['helper.py'],
        local_params=[
            {"prop": "data_path", "direct": "OUT", "type": "VARCHAR", "value": ""}],
        # environment_name="ray-demo"
    )

    task_train_model = Python(
        name="train_model.py",
        definition=load_script("train_model.py"),
        resource_list=['helper.py'],
        local_params=[
            {"prop": "checkpoint_path", "direct": "OUT",
                "type": "VARCHAR", "value": ""},
            {"prop": "dataset_path", "direct": "OUT",
                "type": "VARCHAR", "value": ""}
        ],
        # environment_name="ray-demo"
    )

    task_serving = Python(
        name="serving",
        definition=load_script("serving.py"),
        resource_list=['helper.py'],
        local_params=[
            {"prop": "endpoint_uri", "direct": "OUT", "type": "VARCHAR", "value": ""}]
    )

    task_test_serving = Python(
        name="test_serving",
        definition=load_script("test_serving.py"),
        # environment_name="ray-demo"
    )

    task_get_data >> task_train_model >> task_serving >> task_test_serving

    pd.submit()


with Workflow(
    name="deploy-remote",
    resource_list=[
        resource_helper
    ],
    param={
        "deploy_ray_address": "ray://172.17.0.3:10001",
        "dataset_path": "/tmp/ray-example/data/dataset.pkl",
        'checkpoint_path': "/tmp/ray-example/checkpoint.bin"
    }
) as pd:

    task_serving = Python(
        name="serving",
        definition=load_script("serving.py"),
        resource_list=['helper.py'],
        local_params=[
            {"prop": "endpoint_uri", "direct": "OUT", "type": "VARCHAR", "value": ""}]
    )

    task_test_serving = Python(
        name="test_serving",
        definition=load_script("test_serving.py"),
        # environment_name="ray-demo"
    )

    task_serving >> task_test_serving

    pd.submit()

with Workflow(
    name="start-ray",
) as pd:

    # dowanload data
    task_start = Shell(
        name="start",
        command="""
        ray start --num-cpus=8 --object-store-memory=7000000000 --head --block --dashboard-host=0.0.0.0
        """,
        # environment_name="ray-demo"
    )

    pd.submit()

with Workflow(
    name="stop-ray",
) as pd:

    # dowanload data
    task_start = Shell(
        name="stop",
        command="""
        ray stop
        """,
        # environment_name="ray-demo"
    )

    pd.submit()

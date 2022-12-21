from pydolphinscheduler.tasks import Shell
from pydolphinscheduler.core.workflow import Workflow
from pydolphinscheduler.core.resource import Resource


def load_resource(file_name):
    with open(file_name, 'r') as f:
        content = f.read()

    resource = Resource(name=file_name, content=content)
    return resource


resource_requirement = load_resource("requirements.txt")

with Workflow(
    name="create-env",
    resource_list=[
        resource_requirement
    ],
    param={
        "name": "ray-demo",
        "python_version": "3.8.10",
    }
) as workflow:

    task_create_env = Shell(
        name="create-env",
        command="""
        conda create -n ${name} python=${python_version} -y
        source activate ${name}
        echo $(which pip)
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        """,
        resource_list=['requirements.txt'])

    workflow.submit()

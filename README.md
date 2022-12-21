# dolphinscheduler-ray-example



Demo from [Tabular data training and serving with Keras and Ray AIR](https://docs.ray.io/en/latest/ray-air/examples/tfx_tabular_train_to_serve.html)



## Start DolphinScheduler

We start the Dolphinscheduler with the following command.

The following ports are used for:

- 12345: DolphinScheduler UI
- 25333: pydolphinscheduler SDK to submit the workflow
- 8265: the tray (for training) dash board 

```shell
docker run --name dolphinscheduler-standalone-server -p 12345:12345 -p 25333:25333 -p 8265:8265 -d jalonzjg/dolphinscheduler-standalone-server:3.1.2-ray
```

And then, we can log in to the DolphinScheduler at `http://<ip>:12345/dolphinscheduler/ui`

- user: `admin`

- password: `dolphinscheduler123`


## Create workflow

```shell
python3 -m pip install apache-dolphinscheduler==4.0.0
export PYDS_HOME=./
python3 pyds-workflow.py
```

After we log in to the DolphinScheduler, we can see a project

![image-20221221231830084](images/image-20221221231830084.png)



Then, we can see 3 workflow in the project

- start-ray: start a ray cluster in the docker
- stop-ray: stop the ray cluster
- pipeline: train the model in the local ray cluster and deploy the model

![image-20221222004719448](images/image-20221222004719448.png)



### start ray

![image-20221222004754684](images/image-20221222004754684.png)

Then, we can log in to the ray (for model training) dashboard` <ip>:8265`



### Run Pipeline



![image-20221222004825367](images/image-20221222004825367.png)



**Startup Parameter:**

- train_ray_address: ray cluster address of the training model
- deploy_ray_address: ray cluster address of the deploy model



Then we can seed the workflow instance of `pipeline`, there are for tasks:

- get_data: download data, or you can do something like etl task
- train_model: training model
- serving: deploy model
- test_serving: test the model serving

![image-20221221233418387](images/image-20221221233418387.png)



We can double click the test_serving task and click the view log to view the task log. Log as follows.

![image-20221221233636615](images/image-20221221233636615.png)

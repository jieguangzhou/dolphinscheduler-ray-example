# dolphinscheduler-ray-example


## Start DolphinScheduler



```
docker run --name dolphinscheduler-standalone-server -p 12345:12345 -p 25333:25333 -p 8265:8265 -d dolphinscheduler-standalone-server:3.1.2-ray
```

## Start ray cluster to deploy model

```
docker run --name ray -p 8266:8265 -p 10001:10001 -d dolphinscheduler-standalone-server:3.1.2-ray ray start --num-cpus=8 --object-store-memory=7000000000 --head --block --dashboard-host=0.0.0.0
```


## Create workflow
```
export PYDS_HOME=./
python pyds-workflow.py
```


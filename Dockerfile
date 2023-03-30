FROM jalonzjg/dolphinscheduler-standalone-server:3.1.4-conda

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

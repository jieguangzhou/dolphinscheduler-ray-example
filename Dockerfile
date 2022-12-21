FROM jalonzjg/dolphinscheduler-standalone-server:3.1.2-conda

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

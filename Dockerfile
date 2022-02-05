FROM python:3.9

WORKDIR /home

ENV IDEVTIER_BOT_TOKEN=""

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt ./
COPY *.py ./
COPY config ./config
COPY handlers ./handlers
COPY model ./model
COPY repository ./repository
RUN pip install -U pip && pip install -r requirements.txt && apt-get update && apt-get install sqlite3

ENTRYPOINT ["python", "app.py"]

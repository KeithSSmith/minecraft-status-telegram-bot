FROM python:3.8-slim-buster
ADD . /app
WORKDIR /app
RUN python -m pip install -r /app/requirements.txt
ENV HOSTNAME=""
ENV PORT=""
ENV BOT_TOKEN=""
ENV SERVER_NAME=""
ENTRYPOINT python3 /app/server_monitor.py -s ${HOSTNAME} -p ${PORT} -t ${BOT_TOKEN} -n ${SERVER_NAME}

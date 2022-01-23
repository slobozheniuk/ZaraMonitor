FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ZaraMonitor.py ZaraMonitor.py
COPY ZaraMonitorBot.py ZaraMonitorBot.py
CMD python3 ZaraMonitorBot.py $ZARA_MONITOR_BOT_TOKEN --host=0.0.0.0
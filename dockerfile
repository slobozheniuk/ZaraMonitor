FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN playwright install && playwright install-deps
COPY TestBot.py TestBot.py
COPY ZaraMonitor.py ZaraMonitor.py
COPY ZaraMonitorBot.py ZaraMonitorBot.py
CMD python3 TestBot.py $ZARA_MONITOR_BOT_TOKEN --host=0.0.0.0
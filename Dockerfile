FROM python:3.7

RUN mkdir /usr/src/skale-watchdog
WORKDIR /usr/src/skale-watchdog

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH="/usr/src/skale-watchdog"
CMD ["python", "server.py"]

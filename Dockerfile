FROM python:3

RUN pip install pika requests

COPY nagios_retriever.py /
COPY queue_inspector.py /

CMD python -u /nagios_retriever.py

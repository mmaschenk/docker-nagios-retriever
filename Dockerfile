FROM python:3



COPY requirements.txt /
RUN pip install -r requirements.txt
COPY nagios_retriever.py /
COPY queue_inspector.py /

CMD python -u /nagios_retriever.py

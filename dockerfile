FROM python:3.9

WORKDIR /app
COPY . /app

RUN pip install update
RUN pip install -r requirements.txt


CMD python chatbot.py
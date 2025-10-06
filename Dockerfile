FROM python:3.13.7-slim-trixie

WORKDIR /python-docker

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "start.py"]

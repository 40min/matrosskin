FROM python:3.6.8-jessie

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install dropbox

COPY ./matrosskin ./matrosskin
COPY ./config.yaml ./config.yaml

RUN mkdir ./data

CMD [ "python", "./matrosskin/app.py" ]
FROM python:3.7.4-stretch

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install dropbox

COPY ./config.yaml ./config.yaml
COPY ./gcp_key.json ./gcp_key.json

RUN mkdir ./data

RUN python -m nltk.downloader stopwords

CMD [ "python", "./matrosskin/app.py" ]
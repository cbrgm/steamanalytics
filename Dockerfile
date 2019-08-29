FROM docker.io/library/python:3.7-alpine

ENV SCRAPE_INTERVAL=5 \
    SCRAPE_OFFSET=10 \
    RETHINK_HOST=localhost \
    RETHINK_PORT=28015 \
    RETHINK_DB=steam \
    RETHINK_TABLE=products \
    RETHINK_USER=admin \
    RETHINK_PASS= 

RUN apk update 

WORKDIR /usr/src/app

COPY . ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD python3.7 main.py

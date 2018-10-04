FROM python:3.7-alpine

RUN apk -U add build-base linux-headers libffi-dev  \
    gettext curl gcc musl-dev python3-dev openssl-dev 

RUN mkdir /app
WORKDIR /app
# Add requirements.txt before rest of repo for caching
ADD requirements.txt /app
RUN pip install -rrequirements.txt

ADD . /app/
ENTRYPOINT ["python", "app.py"]

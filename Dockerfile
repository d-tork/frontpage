FROM python:3.10-slim-bullseye
LABEL author="dtorkelson@gmail.com"

WORKDIR /app
RUN pip3 install --upgrade pip setuptools wheel

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

RUN mkdir /cache
VOLUME /cache

COPY . .
RUN pip3 install .

ENTRYPOINT ["gutensearch"]

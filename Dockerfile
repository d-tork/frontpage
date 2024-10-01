FROM python:3.10-slim-bullseye
LABEL author="dtorkelson@gmail.com"

WORKDIR /app
RUN pip3 install --upgrade pip setuptools wheel

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

RUN mkdir /cache
VOLUME /cache

ENV DB_HOST=localhost DB_PORT=3307 MYSQL_ROOT_PASSWORD=my-secret-pw

COPY . .
RUN pip3 install .

ENTRYPOINT ["gutensearch"]

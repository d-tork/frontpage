FROM python:3.10-slim-bullseye
LABEL author="dtorkelson@gmail.com"

WORKDIR /app
RUN pip3 install --upgrade pip setuptools wheel

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# pre-load NLTK stopwords
RUN python -c "import nltk; nltk.download('stopwords')"

RUN mkdir /cache
VOLUME /cache

ENV DB_HOST=gutensearch-db DB_PORT=3306 MYSQL_ROOT_PASSWORD=my-secret-pw

COPY . .
RUN pip3 install .

ENTRYPOINT ["gutensearch"]

# Database custom image
FROM mysql:5-debian
ENV MYSQL_DATABASE=gutensearch

COPY ./scripts/ /docker-entrypoint-initdb.d/

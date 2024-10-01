# Database custom image
FROM mysql:5-debian
ENV MYSQL_DATABASE=gutensearch

COPY mysql.cnf /etc/mysql/conf.d/mysql.cnf
COPY ./scripts/ /docker-entrypoint-initdb.d/

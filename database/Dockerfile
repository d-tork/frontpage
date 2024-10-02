# Database custom image
FROM mysql:5-debian
ENV MYSQL_DATABASE=gutensearch

COPY mysql.cnf /etc/mysql/conf.d/mysql.cnf
COPY gs_backup.sql.gz /tmp/
COPY ./scripts/ /docker-entrypoint-initdb.d/

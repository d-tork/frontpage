# Gutensearch

Get word frequencies from a Project Gutenberg book. 

## Building docker images

### Individually

```
docker build -t gutensearch .
docker build -t pgsql database/
```

### As a docker compose stack

```
docker compose up --build -d
```


## Accessing database directly from host

```
mysql -h localhost -P 3307 --protocol=tcp -D gutensearch -uroot -pmy-secret-pw
```

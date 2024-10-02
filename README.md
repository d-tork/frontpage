# Gutensearch

Get word frequencies from a Project Gutenberg book. 

## Running the app

First start the database in the background and build the executable image
```
docker compose up -d --build
docker build -t gutensearch .
```
Then run the container as an executable, joining the docker compose network
```
docker run -it --network=frontpage_default gutensearch 103 --limit 5
```
A helper script, `runner.sh`, has been provided which bind-mounts a location for cached books.
```
./runner.sh 103 --limit 5
```

## Accessing database directly from host

```
mysql -h localhost -P 3307 --protocol=tcp -D gutensearch -uroot -pmy-secret-pw
```

## Maintenance

### Building docker images

#### Individually

```
docker build -t gutensearch .
docker build -t gutensearch-db database/
```

### Backup and restoration of MySQL (for pre-loading data with the docker image)

#### Export

```
mysqldump -h localhost -P 3307 --protocol=tcp -u root -pmy-secret-pw gutensearch |
	gzip > gs_backup.sql.gz
```

#### Import

```
gunzip < gs_backup.sql.gz | mysql -u root -pmy-secret-pw gutensearch
```

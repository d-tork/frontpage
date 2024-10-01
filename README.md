# Gutensearch

Get word frequencies from a Project Gutenberg book. 

## Running the app

First start the database in the background
```
docker compose up -d --build
```
Then run the container as an executable, joining the docker compose network
```
docker run --network=frontpage_default gutensearch 103 --limit 5
```

Otherwise you'll need to specify environment variables for how the container can access a mysql instance (keeping in mind what the container is able to see on its own network).

## Building docker images

### Individually

```
docker build -t gutensearch .
docker build -t gutensearch-db database/
```

## Accessing database directly from host

```
mysql -h localhost -P 3307 --protocol=tcp -D gutensearch -uroot -pmy-secret-pw
```

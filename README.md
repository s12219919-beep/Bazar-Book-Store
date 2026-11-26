# Bazar Book Store

## Distributed Systems - Lab 1

Bazar is a distributed online bookstore implemented
using Python, Flask, SQLite, REST APIs and Docker.

## Team Members

- Fatima
- Jana

## System Architecture

The system consists of three microservices:

- Frontend Service (Port 5000)
- Catalog Service (Port 5001)
- Order Service (Port 5002)

The services communicate using HTTP REST APIs
through a shared Docker network.

## Requirements

- Docker
- Docker Compose

## How to Run

Clone the repository:

```bash
git clone https://github.com/s12219919-beep/Bazar-Book-Store.git
cd Bazar-Book-Store
```

Start all services:

```bash
sudo docker compose up --build -d
```

Check running services:

```bash
sudo docker compose ps
```

## API Examples

Search books:

```bash
curl http://localhost:5000/search/distributed%20systems
```

Get book information:

```bash
curl http://localhost:5000/info/2
```

Purchase a book:

```bash
curl -X POST http://localhost:5000/purchase/2
```

## Concurrency

SQLite transactions using BEGIN IMMEDIATE are used
to protect stock updates and prevent lost updates
during concurrent purchases.

## Data Persistence

Docker volumes are used to preserve the catalog
and order databases.

## Testing

The system was tested for search, book information,
purchases, invalid book IDs, insufficient stock
and concurrent purchases.

Testing results are available in docs/output.txt.

## Known Limitations

The system does not provide authentication or
automatic failover.

A failure between updating the catalog stock and
saving the order may cause inconsistent data.

## Stop the System

```bash
sudo docker compose down
```

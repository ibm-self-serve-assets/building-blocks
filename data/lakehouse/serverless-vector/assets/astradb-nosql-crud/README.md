# Astra DB NoSQL CRUD Service

**IBM Products**: IBM watsonx.data — Astra DB service
**Language**: Python 3.12
**Framework**: FastAPI

## Overview

FastAPI service providing full CRUD operations on **DataStax Astra DB** NoSQL collections using the `astrapy` Data API with MongoDB-style filter expressions. The Astra DB service is available through IBM watsonx.data.

## Prerequisites

- Astra DB service/database provisioned through IBM watsonx.data
- Astra DB API Endpoint URL
- Astra DB Application Token

## Quick Start

```bash
cp .env.example .env
# Edit .env — set ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `ASTRA_DB_API_ENDPOINT` | Astra DB API endpoint URL | `https://<db-id>-<region>.apps.astra.datastax.com` |
| `ASTRA_DB_APPLICATION_TOKEN` | Astra DB application token | `AstraCS:...` |
| `ASTRA_DB_KEYSPACE` | Default keyspace (optional) | `default_keyspace` |
| `REST_API_KEY` | API key for this service | any secret string |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/collections/insert` | Insert one or many documents |
| `POST` | `/collections/find` | Query with MongoDB-style filters |
| `POST` | `/collections/update` | Update with `$set`, `$unset`, `$inc` operators |
| `POST` | `/collections/delete` | Delete documents matching filter |

## Usage Examples

**Insert documents**:
```bash
curl -X POST http://localhost:8080/collections/insert \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "customers",
    "documents": [
      {"_id": "c001", "name": "IBM Corp", "region": "us-south", "tier": "enterprise"},
      {"_id": "c002", "name": "Acme Inc", "region": "eu-de", "tier": "standard"}
    ]
  }'
```

**Query with filters**:
```bash
curl -X POST http://localhost:8080/collections/find \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "customers", "filter": {"region": {"$eq": "us-south"}}, "limit": 20}'
```

**Update documents**:
```bash
curl -X POST http://localhost:8080/collections/update \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "customers", "filter": {"_id": "c001"}, "update": {"$set": {"tier": "premium"}}}'
```

**Delete documents**:
```bash
curl -X POST http://localhost:8080/collections/delete \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "customers", "filter": {"tier": {"$eq": "standard"}}}'
```

## Docker Deployment

```bash
docker build -t astradb-nosql-crud .
docker run -p 8080:8080 --env-file .env astradb-nosql-crud
```

## Project Structure

```
astradb-nosql-crud/
├── main.py                          # FastAPI app entrypoint
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── route/
    │   └── collections/routes.py    # CRUD endpoints
    └── src/
        ├── model/DocumentModel.py   # Pydantic request/response models
        ├── services/CRUDService.py  # astrapy Data API operations
        └── utils/                   # Config and client utilities
```

## IBM Cloud References

- [IBM watsonx.data — Astra DB service](https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service)
- [DataStax Astra DB Data API Reference](https://docs.datastax.com/en/astra/astra-db-vector/api-reference/data-api.html)
- [astrapy SDK Documentation](https://github.com/datastax/astrapy)

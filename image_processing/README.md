# Playground

# Setup

Install poetry and poe:

```
curl -sSL https://install.python-poetry.org | python -
pip install poethepoet
```

Run MinIO storage locally:

```
docker run -d --restart=always \
   -p 9000:9000 \
   -p 9001:9001 \
   --name minio \
   -v ~/data:/data \
   -e "MINIO_ROOT_USER=admin" \
   -e "MINIO_ROOT_PASSWORD=123456789" \
   quay.io/minio/minio server /data --console-address ":9001"
```

# Structure

1. API where you upload an image (FastAPI) store it and then send it to Kafka topic to calculate a vector
2. Once the vector is calculated -> trigger calculation of features.

embeddings

#

3 Topics:

```
image_processing - incomming messages
image_processing.result - processed messages
image_processing.dead_letter_queue - failed to process
```

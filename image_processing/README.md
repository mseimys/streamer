# Playground

# Setup

Install poetry and poe:

```
curl -sSL https://install.python-poetry.org | python -
pip install poethepoet
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

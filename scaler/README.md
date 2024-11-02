# Kafka Tests

## Goals

Figure out how scaling works and how partition rebalancing impacts speed, how acks are handled.

## Scenario 1

We have 1 constant producer of message - `producer.py`
We have a consumer that takes 2 seconds to consume the message - `consumer.py`
We need to figure out how to detect that each messages was properly handled.

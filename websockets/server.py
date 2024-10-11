import asyncio
import signal
from aiokafka import AIOKafkaConsumer
import websockets

# Set of connected WebSocket clients
connected_clients = set()

# Kafka consumer configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "busdata"

HOST = "localhost"
PORT = 8080


async def kafka_consumer():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="websocket-server-group",
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = msg.value.decode("utf-8")
            # Broadcast message to all connected clients
            if connected_clients:
                await asyncio.gather(*(client.send(message) for client in connected_clients))
    except Exception as e:
        print(f"Kafka consumer error: {e}")
    finally:
        await consumer.stop()


async def websocket_handler(websocket, path):
    # Register client
    connected_clients.add(websocket)
    print(f"New client connected: {websocket.remote_address}")
    try:
        async for _ in websocket:
            pass  # The server does not expect messages from clients
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Unregister client
        connected_clients.remove(websocket)


def main():
    loop = asyncio.get_event_loop()

    # Start Kafka consumer
    loop.create_task(kafka_consumer())

    # Start WebSocket server
    server = websockets.serve(websocket_handler, HOST, PORT)
    loop.run_until_complete(server)
    print(f"Websocket server is running on ws://{HOST}:{PORT}")

    # Graceful shutdown handling
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, loop.stop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Websocket server is shutting down...")
    finally:
        loop.close()


if __name__ == "__main__":
    main()

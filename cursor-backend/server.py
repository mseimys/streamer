#!/usr/bin/env python

import json
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import websockets
from aiohttp import web

HOST = "localhost"
PORT = 8080
HTTP_PORT = 8000

# Kafka consumer configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "cursor"

# Set of connected WebSocket clients
connected_clients = set()


def make_client_id(websocket):
    return f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"


async def kafka_consumer(consumer):
    try:
        async for msg in consumer:
            message = msg.value.decode("utf-8")
            # Broadcast message to all connected clients
            if connected_clients:
                await asyncio.gather(
                    *(
                        client.send(message)
                        for client in connected_clients
                        if make_client_id(client) != json.loads(message)["client"]
                    )
                )
    except Exception as e:
        print(f"Kafka consumer error: {e}")
    finally:
        await consumer.stop()


async def websocket_handler(websocket, path, producer):
    # Register client
    connected_clients.add(websocket)
    print(f"New client connected: {websocket.remote_address}")
    try:
        async for msg in websocket:
            message = json.loads(msg)
            message["client"] = make_client_id(websocket)
            print("Got message from client:", message)
            await producer.send_and_wait(KAFKA_TOPIC, json.dumps(message).encode("utf-8"))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Unregister client
        connected_clients.remove(websocket)


async def handle_heatmap(request):
    return web.FileResponse("heatmap.png")


async def main():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="websocket-server-group",
        auto_offset_reset="latest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    await consumer.start()
    await producer.start()

    consumer_task = asyncio.create_task(kafka_consumer(consumer))
    server = await websockets.serve(lambda ws, path: websocket_handler(ws, path, producer), HOST, PORT)
    print(f"WebSocket server is running on ws://{HOST}:{PORT}")

    app = web.Application()
    app.router.add_get("/heatmap.png", handle_heatmap)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, HTTP_PORT)
    await site.start()
    print(f"HTTP server is running on http://{HOST}:{HTTP_PORT}")

    try:
        await asyncio.Future()  # run forever
    except asyncio.CancelledError:
        print("Server shutting down...")
        consumer_task.cancel()
        await consumer.stop()
        await producer.stop()
        server.close()
        await server.wait_closed()
        await runner.cleanup()
        print("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())

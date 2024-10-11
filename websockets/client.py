import json
import asyncio
import websockets


async def listen():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server")
        try:
            end_time = asyncio.get_event_loop().time() + 10
            async for message_raw in websocket:
                message = json.loads(message_raw)
                print(f"{asyncio.get_event_loop().time()} Received message: {message['id']}")
                if asyncio.get_event_loop().time() > end_time:
                    break
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")


if __name__ == "__main__":
    asyncio.run(listen())
